import streamlit as st
from openai import OpenAI
import ollama

# Setting up page configuration
st.set_page_config(
    page_title="Chat Playground",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

def extract_model_names(models_info: list) -> tuple:
    return tuple(model["name"] for model in models_info["models"])

def main():
    # Initializing OpenAI client
    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama"
    )

    # Fetching available models from Ollama
    models_info = ollama.list()
    available_models = extract_model_names(models_info)

    # Displaying model selection dropdown
    selected_model = st.selectbox(
        "Pick a model available locally on your system ↓", 
        available_models if available_models else ["No models available"]
    )

    # Displaying warning if no models are available
    if not available_models:
        st.warning("You have not pulled any model from Ollama yet!")
        if st.button("Go to settings to download a model"):
            st.page_switch("pages/03_⚙️_Settings.py")

    # Creating message container
    message_container = st.container(height=500, border=True)

    # Initializing session state for messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Displaying chat messages
    for message in st.session_state.messages:
        avatar = "🤖" if message["role"] == "assistant" else "😎"
        with message_container.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Collecting user input prompt
    if prompt := st.chat_input("Enter a prompt here..."):
        try:
            # Adding user input to messages
            st.session_state.messages.append(
                {"role": "user", "content": prompt}
            )

            # Displaying user input in chat
            message_container.chat_message("user", avatar="😎").markdown(prompt)

            # Generating response from AI model
            with message_container.chat_message("assistant", avatar="🤖"):
                with st.spinner("Model working..."):
                    stream = client.chat.completions.create(
                        model=selected_model,
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ],
                        stream=True,
                    )
                # Streaming response
                response = st.write_stream(stream)
            # Adding AI response to messages
            st.session_state.messages.append(
                {"role": "assistant", "content": response}
            )

        except Exception as e:
            st.error(e, icon="⛔️")

if __name__ == "__main__":
    main()
