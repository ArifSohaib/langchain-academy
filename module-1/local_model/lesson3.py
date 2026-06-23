# alternate version because the one from course uses "LangSmith" subscription which I don't want
# replaced with https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps
import random
from typing import Literal, TypedDict

import streamlit as st
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph


class State(TypedDict):
    graph_state: str


def node_1(state):
    print("__Node 1__")
    return {"graph_state": state["graph_state"] + "\nI am"}


def node_2(state):
    print("__Node 2__")
    return {"graph_state": f"{state['graph_state']} happy!"}


def node_3(state):
    print("__Node 3__")
    return {"graph_state": f"{state['graph_state']} sad!"}


def decide_mood(state) -> Literal["node_2", "node_3"]:
    user_input = state["graph_state"]
    print(f"user_input:{user_input}")
    if random.random() < 0.5:
        return "node_2"
    return "node_3"


def create_graph():
    builder = StateGraph(State)
    builder.add_node("node_1", node_1)
    builder.add_node("node_2", node_2)
    builder.add_node("node_3", node_3)

    builder.add_edge(START, "node_1")
    builder.add_conditional_edges("node_1", decide_mood)
    builder.add_edge("node_2", END)
    builder.add_edge("node_3", END)
    graph = builder.compile()
    return graph


def response_generator(graph: CompiledStateGraph, input_str: str):
    response = graph.invoke({"graph_state": input_str})

    yield response["graph_state"]


st.title("LangGraph simple chain")
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

graph = create_graph()
with st.sidebar:
    img_bytes = graph.get_graph().draw_mermaid_png()
    st.image(img_bytes)

if prompt := st.chat_input("What is up?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator(graph, prompt))
    st.session_state.messages.append({"role": "assistant", "content": response})
