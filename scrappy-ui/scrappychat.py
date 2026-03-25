import streamlit as st
import random
import time
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from ..scrappy-ai-investigator.app.agents.intent_agent import system_prompt


template = system_prompt
prompt = ChatPromptTemplate.from_template(template)

#Load the local Llama3.2 model
model = OllamaLLM(model="llama3.2")
chain = prompt | model


st.title("Scrappy Market AI Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if user_input := st.chat_input("How can I help you?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_input)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

# Streamed response emulator
def response_generator():
    response = chain.invoke({"question": user_input})
    for word in response.split():
        yield word + " "
        time.sleep(0.05)

# Display assistant response in chat message container
with st.chat_message("assistant"):
    response = st.write_stream(response_generator())
# Add assistant response to chat history
st.session_state.messages.append({"role": "assistant", "content": response})