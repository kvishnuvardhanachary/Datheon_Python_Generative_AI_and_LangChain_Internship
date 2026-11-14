import streamlit as st  # type: ignore[reportMissingImports]

from agent import agent


# Page Configuration

st.set_page_config(
    page_title="AI Agent Chatbot",
    page_icon="🤖",
    layout="wide"
)


# Application Title

st.title("🤖 AI Agent Chatbot")

st.caption(
    "Powered by Python, LangChain, Google Gemini AI and Streamlit"
)


# Sidebar

with st.sidebar:

    st.header("⚙️ Settings")

    st.success("Gemini AI Connected")

    st.write("Available Tools:")

    st.write("🌐 Internet Search")

    st.write("🧮 Calculator")

    st.write("📁 Notes Reader")

    st.divider()

    if st.button("🗑️ Clear Chat"):

        st.session_state.messages = []

        st.rerun()


# Initialize Session State

if "messages" not in st.session_state:

    st.session_state.messages = []


# Display Previous Messages

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# Chat Input

user_input = st.chat_input(
    "Ask me anything..."
)


if user_input:

    # Display User Message

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):

        st.markdown(user_input)


    # AI Response

    with st.chat_message("assistant"):

        response_placeholder = st.empty()

        try:

            def generate_response():

                conversation = [
                    {
                        "role": message["role"],
                        "content": message["content"]
                    }
                    for message in st.session_state.messages
                ]

                for chunk, metadata in agent.stream(
                    {"messages": conversation},
                    stream_mode="messages"
                ):

                    # Only display AI-generated text

                    if chunk.type == "AIMessageChunk":

                        content = chunk.content

                        if isinstance(content, str) and content:

                            yield content

                        elif isinstance(content, list):

                            for item in content:

                                if (
                                    isinstance(item, dict)
                                    and item.get("type") == "text"
                                ):

                                    yield item["text"]


            # Stream response in real time

            response = st.write_stream(
                generate_response()
            )

            # Save assistant response

            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })

        except Exception as e:

            st.error(f"Error: {str(e)}")