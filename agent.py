import os
import ast
import operator


def load_dotenv(path=".env"):
    """Load simple KEY=VALUE entries without requiring python-dotenv."""
    try:
        with open(path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if key:
                    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
                        value = value[1:-1]
                    os.environ.setdefault(key, value)
    except FileNotFoundError:
        pass

try:
    ChatGoogleGenerativeAI = __import__(
        "langchain_google_genai", fromlist=["ChatGoogleGenerativeAI"]
    ).ChatGoogleGenerativeAI
except ImportError as exc:
    raise ImportError(
        "Install the Google GenAI integration with `pip install langchain-google-genai`."
    ) from exc
create_agent = __import__("langchain.agents", fromlist=["create_agent"]).create_agent
tool = __import__("langchain_core.tools", fromlist=["tool"]).tool

try:
    DuckDuckGoSearchRun = __import__(
        "langchain_community.tools", fromlist=["DuckDuckGoSearchRun"]
    ).DuckDuckGoSearchRun
except ImportError as exc:
    raise ImportError(
        "Install the community tools with `pip install langchain-community`."
    ) from exc


load_dotenv()


# Gemini API configuration

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    streaming=True
)


# Tool 1: Internet Search

search_tool = DuckDuckGoSearchRun()


@tool
def web_search(query: str) -> str:
    """Search the internet for current information."""

    return search_tool.run(query)


# Tool 2: Calculator

operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod
}


def calculate_expression(node):

    if isinstance(node, ast.Constant):
        if type(node.value) in (int, float):
            return node.value

    elif isinstance(node, ast.BinOp):

        operation = operators.get(type(node.op))

        if operation is None:
            raise ValueError("Unsupported operation")

        return operation(
            calculate_expression(node.left),
            calculate_expression(node.right)
        )

    elif isinstance(node, ast.UnaryOp):

        if isinstance(node.op, ast.USub):
            return -calculate_expression(node.operand)

        if isinstance(node.op, ast.UAdd):
            return calculate_expression(node.operand)

    raise ValueError("Invalid mathematical expression")


@tool
def calculator(expression: str) -> str:
    """Calculate mathematical expressions such as 25*10 or 100/5."""

    try:

        tree = ast.parse(expression, mode="eval")

        result = calculate_expression(tree.body)

        return str(result)

    except Exception as e:

        return f"Calculation error: {e}"


# Tool 3: Read Local Notes

@tool
def read_notes(query: str) -> str:
    """Read information from the local notes.txt file."""

    try:

        with open("notes.txt", "r", encoding="utf-8") as file:

            content = file.read()

        return content

    except FileNotFoundError:

        return "notes.txt file not found."


# Register all tools

tools = [
    web_search,
    calculator,
    read_notes
]


# Create AI Agent

agent = create_agent(
    model=model,
    tools=tools,
    system_prompt="""
    You are a helpful AI assistant.

    You can:
    1. Search the internet.
    2. Perform mathematical calculations.
    3. Read local notes.

    Use the appropriate tools whenever necessary.

    Give clear and understandable answers.
    """
)


def calculate_expression(node):

    if isinstance(node, ast.Constant):
        if type(node.value) in (int, float):
            return node.value

    elif isinstance(node, ast.BinOp):

        operation = operators.get(type(node.op))

        if operation is None:
            raise ValueError("Unsupported operation")

        return operation(
            calculate_expression(node.left),
            calculate_expression(node.right)
        )

    elif isinstance(node, ast.UnaryOp):

        if isinstance(node.op, ast.USub):
            return -calculate_expression(node.operand)

        if isinstance(node.op, ast.UAdd):
            return calculate_expression(node.operand)

    raise ValueError("Invalid mathematical expression")


@tool
def calculator(expression: str) -> str:
    """Calculate mathematical expressions such as 25*10 or 100/5."""

    try:

        tree = ast.parse(expression, mode="eval")

        result = calculate_expression(tree.body)

        return str(result)

    except Exception as e:

        return f"Calculation error: {e}"


# Tool 3: Read Local Notes

@tool
def read_notes(query: str) -> str:
    """Read information from the local notes.txt file."""

    try:

        with open("notes.txt", "r", encoding="utf-8") as file:

            content = file.read()

        return content

    except FileNotFoundError:

        return "notes.txt file not found."


# Register all tools

tools = [
    web_search,
    calculator,
    read_notes
]


# Create AI Agent

agent = create_agent(
    model=model,
    tools=tools,
    system_prompt="""
    You are a helpful AI assistant.

    You can:
    1. Search the internet.
    2. Perform mathematical calculations.
    3. Read local notes.

    Use the appropriate tools whenever necessary.

    Give clear and understandable answers.
    """
)
