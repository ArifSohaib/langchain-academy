# %%
from typing import List

from IPython.display import Image, Markdown, display
from langchain_core.messages import HumanMessage
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
builder.add_edge("tools", "tool_calling_llm")
builder.add_edge("tools", END)
builder.add_edge("tool_calling_llm", END)
graph = builder.compile()
# %%
display(Image(graph.get_graph().draw_mermaid_png()))
# %%
messages: List[AnyMessage] = [
    HumanMessage(content="testing basic tool call what is 1024 multiplied by 64")
]
simple_result = graph.invoke({"messages": messages})
# %%
for m in simple_result["messages"]:
    print(f"{m.id}")
    m.pretty_print()
# %%
for m in messages:
    print(f"{m.id}")

# %%
messages = simple_result["messages"]
# %%
for m in messages:
    display(Markdown(m.pretty_print()))
# %%
messages.append(
    HumanMessage(
        content="While the total is less than 10,000 multiple the values in the list [102, 100, 200, 150, 101, 90, 101,100,110,110,] by 10 and keep adding. What does the total come out to BEFORE reaching 10,000. Use the provided tools"
    )
)
# %%

complex_result = graph.invoke({"messages": messages})

# %%
messages = complex_result["messages"]

for m in messages:
    m.pretty_print()
# %%
