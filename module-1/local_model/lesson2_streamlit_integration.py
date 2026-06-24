# part 2 of lesson 2, replacing the statig graph with ollama model without memory


from typing import TypedDict

import streamlit as st
from langchain_ollama import ChatOllama

llm = ChatOllama(model="gemma4:e4b")


class State(TypedDict):
    graph_state: str


st.title("LangGraph local model")
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def generate_response(prompt: str):
    response = llm.invoke(prompt)
    yield response.content


if prompt := st.chat_input("What is up?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        response = st.write_stream(generate_response(prompt))
    st.session_state.messages.append({"role": "assistant", "content": response})
