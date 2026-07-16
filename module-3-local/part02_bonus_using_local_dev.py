"""
Using the local dev server for langgraph
Note that this one does not use the REPL
start this server by using cd into `module-3-local` and running `uv run langgraph dev`
"""
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage
from langgraph.graph import START, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.state import StateGraph
from simple_tools import add, multiply, divide, sub, pow, apply_to_list
from pathlib import Path
import sqlite3


llm = ChatOllama(model="gemma4:e4b")
tools = [add,multiply, divide, sub, pow, apply_to_list]
llm_with_tools = llm.bind_tools(tools)


sys_message = SystemMessage(content="you are a helpful assistant used to perform scalar and vector math on sets of inputs")
def assistant(state:MessagesState):
    return {"messages":[llm_with_tools.invoke([sys_message]+state["messages"])]}

builder = StateGraph(MessagesState)
builder.add_node("assistant",assistant)
builder.add_node("tools",ToolNode(tools))
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant",tools_condition)
builder.add_edge("tools","assistant")
db_path = Path("state_db","example.db")
conn = sqlite3.connect(str(db_path), check_same_thread=False)

graph = builder.compile(interrupt_before=["tools"])
graph.get_graph().draw_mermaid_png()
