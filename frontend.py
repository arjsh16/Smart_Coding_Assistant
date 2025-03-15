
from details import *
import streamlit as st
from stack_gemini import main
from memory import *

st.markdown("""
<style>
    html, body, [class*="st-"] {
    font-family: 'IBM Plex Mono', monospace;
    background-color: #1E1E2E;  /* Dark purple-blue */
    color: #ECEFF4;  /* Soft white */
}

.user-message {
    color: #A3BE8C; /* Soft green */
}

.bot-message {
    color: #D8DEE9; /* Soft white */
}

.code-response {
    background-color: #2E3440;  /* Dark grey-blue */
    color: #81A1C1;  /* Cool blue */
    padding: 10px;
    border-radius: 5px;
}
</style>
""", unsafe_allow_html=True)

st.title("AI :blue[Agent]")
st.markdown(":grey[Welcome to the AI Agent for code generation. Ask me anything!]")

if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    st.chat_message(message['role']).markdown(message['content'])

prompt = st.chat_input('Your Prompt goes here')

if prompt:
    st.chat_message('user').markdown(prompt)
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    generated_text = main(prompt)
    save_old_messages(prompt, generated_text)
    st.chat_message('assistant').markdown(generated_text)
    st.session_state.messages.append({'role': 'assistant', 'content': generated_text})
