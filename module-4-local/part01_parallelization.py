# %%
from IPython.display import display, Image
from langchain.messages import AIMessage, SystemMessage, HumanMessage, AnyMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.errors import EmptyInputError
from langchain_ollama import ChatOllama
from typing import TypedDict, Annotated, Any
from operator import add
from langchain_tavily import TavilySearch
from langgraph.errors import InvalidUpdateError, NodeInterrupt
from langchain_core.documents import Document
from utils import get_wiki_content
import json
import operator
from typing import Annotated
from langgraph.types import Send
# %%
class State(TypedDict):
    state: Annotated[list[str], add]
class ReturnNodeValue:
    def __init__(self, node_secret:str):
        self._value = node_secret
    def __call__(self, state:State)->Any:
        print(f"Adding {self._value} to {state['state']}")
        return {"state":[self._value]}
# %%

builder_sequential = StateGraph(State)
builder_sequential.add_node("a",ReturnNodeValue("I'm A"))
builder_sequential.add_node("b",ReturnNodeValue("I'm B"))
builder_sequential.add_node("c",ReturnNodeValue("I'm C"))
builder_sequential.add_node("d",ReturnNodeValue("I'm D"))
builder_sequential.add_edge(START, "a")
builder_sequential.add_edge("a","b")
builder_sequential.add_edge("b","c")
builder_sequential.add_edge("c","d")
builder_sequential.add_edge("d", END)
graph_sequential = builder_sequential.compile()
display(Image(graph_sequential.get_graph().draw_mermaid_png()))
# %%
result1 = graph_sequential.invoke({"messages":[]})
# %%
builder_parallel = StateGraph(State)
builder_parallel.add_node("a",ReturnNodeValue("I'm A"))
builder_parallel.add_node("b",ReturnNodeValue("I'm B"))
builder_parallel.add_node("c",ReturnNodeValue("I'm C"))
builder_parallel.add_node("d",ReturnNodeValue("I'm D"))
builder_parallel.add_edge(START, "a")
builder_parallel.add_edge("a","b")
builder_parallel.add_edge("a","c")
builder_parallel.add_edge("b","d")
builder_parallel.add_edge("c","d")
builder_parallel.add_edge("d", END)
graph_parallel = builder_parallel.compile()
display(Image(graph_parallel.get_graph().draw_mermaid_png()))
# %%
result_parallel1 = graph_parallel.invoke({"state":[]})
print(result_parallel1)
# %%
builder_multi_stepb = StateGraph(State)

# Initialize each node with node_secret
builder_multi_stepb.add_node("a", ReturnNodeValue("I'm A"))
builder_multi_stepb.add_node("b", ReturnNodeValue("I'm B"))
builder_multi_stepb.add_node("b2", ReturnNodeValue("I'm B2"))
builder_multi_stepb.add_node("c", ReturnNodeValue("I'm C"))
builder_multi_stepb.add_node("d", ReturnNodeValue("I'm D"))

# Flow
builder_multi_stepb.add_edge(START, "a")
builder_multi_stepb.add_edge("a", "b")
builder_multi_stepb.add_edge("a", "c")
builder_multi_stepb.add_edge("b", "b2")
builder_multi_stepb.add_edge(["b2", "c"], "d")
builder_multi_stepb.add_edge("d", END)
graph_multi_stepb = builder_multi_stepb.compile()

display(Image(graph_multi_stepb.get_graph().draw_mermaid_png()))

# %%
print(graph_multi_stepb.invoke({"state":[]}))
# %%
print(graph_multi_stepb.invoke({"state":[]}))
# %%

# %%
