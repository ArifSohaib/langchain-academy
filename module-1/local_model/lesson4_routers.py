# %%
from typing import List

from IPython.display import Image, Markdown, display
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.messages.utils import AnyMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from tool_functions import add, divide, multiply, pow, tool_list

# %%
llm = ChatOllama(model="gemma4:e4b")
llm_with_tools = llm.bind_tools(tool_list)


# conditional tool calling
def tool_calling_llm(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


# %%
builder = StateGraph(MessagesState)
builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_node("tools", ToolNode([multiply, add, divide, pow]))
builder.add_edge(START, "tool_calling_llm")
builder.add_conditional_edges("tool_calling_llm", tools_condition)

builder.add_edge("tools", END)
graph = builder.compile()
# %%
display(Image(graph.get_graph().draw_mermaid_png()))
# %%
mesaages: List[AnyMessage] = [
    HumanMessage(content="testing basic tool call what is 1024 multiplied by 64")
]
messages = graph.invoke({"messages": mesaages})
# %%
for m in messages["messages"]:
    display(Markdown(m.pretty_print()))
# %%
