import os
import json
import sys
from pathlib import Path

from google import genai
from google.genai import types

from pydantic import BaseModel, Field
from dotenv import load_dotenv

#Step 1: Load API key
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")
client = genai.Client(api_key=API_KEY, http_options={'api_version': 'v1beta'})


#Step 2: Resume Date Schema
class EducationItem(BaseModel):
    degree: str = Field(..., description="Degree or qualification obtained")
    institution: str = Field(..., description="Name of the school or university")
    year: str = Field(None, description="Year of graduation or attendance")

class ExperienceItem(BaseModel):
    title: str = Field(None, description="Job title or role")
    company: str = Field(None, description="Company or organization name")
    duration: str = Field(None, description="Duration of employment")
    description: str = Field(None, description="Brief description of responsibilities")

class ResumeData(BaseModel):
    name: str = Field(..., description="Full name of the candidate")
    email: str = Field(..., description="Email address of the candidate")
    phone: str = Field(..., description="Phone number of the candidate")
    education: list[EducationItem] = Field(..., description="List of educational qualifications")
    experience: list[ExperienceItem] = Field(..., description="List of work experiences")
    skills: list[str] = Field(..., description="List of skills possessed by the candidate")
    certifications: list[str] = Field(..., description="List of certifications obtained by the candidate")

    @classmethod
    def model_json_schema(cls, *args, **kwargs):
        schema = super().model_json_schema(*args, **kwargs)
        # Recursively remove 'additionalProperties' from the schema
        def remove_additional_properties(obj):
            if isinstance(obj, dict):
                obj.pop('additionalProperties', None)
                for key, value in obj.items():
                    remove_additional_properties(value)
            elif isinstance(obj, list):
                for item in obj:
                    remove_additional_properties(item)        
        remove_additional_properties(schema)
        return schema


class InvoiceItem(BaseModel):
    item: str = Field(..., description="Item description")
    quantity: str = Field(..., description="Item quantity")
    unit_price: str = Field(..., description="Price per unit")
    total_price: str = Field(..., description="Total price for the item")


class InvoiceData(BaseModel):
    invoice_number: str = Field(..., description="Invoice number")
    invoice_date: str = Field(..., description="Invoice date")
    vendor_name: str = Field(..., description="Vendor name")
    customer_name: str = Field(..., description="Customer name")
    items: list[InvoiceItem] = Field(..., description="Invoice line items")
    subtotal: str = Field(..., description="Invoice subtotal")
    tax: str = Field(..., description="Invoice tax")
    total_amount: str = Field(..., description="Invoice total amount")

#Step 3: Prompt Template

PROMPTS = {
    "resume": """
    You are an expert resume analyzer.

    Extract the following information:

    - Candidate name
    - Email
    - Phone
    - Education
    - Technical skills
    - Experience
    - Projects
    - Certifications

    Rules:

    1. Extract only information in the resume.
    2. Never invent information.
    3. If information is missing, use "Not found".
    4. Return valid structured JSON.

    Example:

    Input:
    Name: Kiran Kumar
    Skills: Python, SQL,Django, Flask, JavaScript, React, Node.js

    Output:
    Candidate name: Kiran Kumar
    Technical skills: Python, SQL,Django, Flask, JavaScript, React, Node.js

    Resume:

    {document}
    """,

    "invoice": """
    You are an expert invoice analyzer.

    Extract the following information:

    - Invoice number
    - Invoice date
    - Vendor name
    - Customer name
    - Items
    - Quantity
    - Unit price
    - Total price
    - Subtotal
    - Tax
    - Total amount

    Rules:

    1. Extract only information in the invoice.
    2. Never invent missing information.
    3. Use "Not found" for missing values.
    4. Preserve original currency and amounts.
    5. Return valid structured JSON.

    Invoice:

    {document}
    """
}

#Step 4: Read Document

def read_document(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        document = file.read()
    if not document.strip():
        raise ValueError("Document is empty")  
    return document

#Step 6: Extract Information using Gemini

def extract_information(document, document_type):
    if document_type not in PROMPTS:
        raise ValueError("Choose  'resume' or 'invoice'")

    prompt = PROMPTS[document_type].format(document=document)
    if document_type == "resume":

        schema = ResumeData

    else:

         schema = InvoiceData

    print("\nGemini is analyzing your document...")

    response = client.models.generate_content(

        model="gemini-2.5-flash",

        contents=prompt,

        config=types.GenerateContentConfig(

            response_mime_type="application/json",

            response_schema=schema

        )
    )

    if not response.text:

        raise ValueError("Empty Gemini response!")

    # Validate JSON using Pydantic

    result = schema.model_validate_json(
        response.text
    )

    return result


# STEP 7: Save JSON Output

def save_output(data, document_type):

    os.makedirs("output", exist_ok=True)

    filename = (
        f"output/{document_type}_output.json"
    )    
    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data.model_dump(),
            file,
            indent=4
        )

    print("\nOutput saved successfully!")

    print("File:", filename)


# STEP 8: Main Function

def main():
    # If you only pass 1 argument (the filename), handle it here:
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_resume_file>")
        return

    file_path = sys.argv[1]
    document_type = "resume"  # default type

    try:

        document = read_document(file_path)

        result = extract_information(
            document,
            document_type
        )

        print("\n========== EXTRACTED JSON ==========")

        print(
            json.dumps(
                result.model_dump(),
                indent=4
            )
        )

        save_output(
            result,
            document_type
        )

    except Exception as error:

        print("\nERROR:", error)


# STEP 9: Execute Program

if __name__ == "__main__":

    main()

