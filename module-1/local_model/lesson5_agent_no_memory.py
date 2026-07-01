# %%
from typing import List

from IPython.display import Image, Markdown, display
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.messages.utils import AnyMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, MessagesState
from langgraph.graph.state import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from test_questions import (
    complex_question,
    multiple_step_question,
    simple_question,
    text_simple_question,
)
from tool_functions import tool_list

# %%
llm = ChatOllama(model="gemma4:e4b")
llm_with_tools = llm.bind_tools(tool_list)

# %%
sys_message = SystemMessage(
    content="You are a helpful assistant tasked with selecting and optionally combining arithmatic operations on scalars or vectors using the provided tools."
)


# %%
def assistrant(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([sys_message] + state["messages"])]}


# %%
builder = StateGraph(MessagesState)
builder.add_node("assistant", assistrant)
builder.add_node("tools", ToolNode(tool_list))

builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")
react_graph = builder.compile()

# %%
display(Image(react_graph.get_graph(xray=True).draw_mermaid_png()))
# %%
messages_simple: List[AnyMessage] = [HumanMessage(content=simple_question)]
messages_simple_result = react_graph.invoke({"messages": messages_simple})

for m in messages_simple_result["messages"]:
    display(Markdown(m.content))
# %%
messages_multistep: List[AnyMessage] = [HumanMessage(content=multiple_step_question)]
messages_multistep_result = react_graph.invoke({"messages": messages_multistep})
# %%
for m in messages_multistep_result["messages"]:
    display(Markdown(m.content))
# print(messages)
# %%
messages_complex: List[AnyMessage] = [HumanMessage(content=complex_question)]
messages_complex_result = react_graph.invoke({"messages": messages_complex})
for m in messages_complex_result["messages"]:
    display(Markdown(m.pretty_print()))

# %%

messages_string: List[AnyMessage] = [HumanMessage(content=text_simple_question)]
messages_string_result = react_graph.invoke({"messages": messages_string})
# %%
for m in messages_string_result["messages"]:
    m.pretty_print()

# %%
print(messages_string)
# %%
