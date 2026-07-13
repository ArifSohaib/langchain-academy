# %%
from typing import List

from IPython.display import Image, display
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.messages.utils import AnyMessage
from langchain_core.runnables.config import RunnableConfig
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState
from langgraph.graph.state import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from test_questions import (
    complex_question,
    complex_question_followup,
)
from tool_functions import tool_list

# %%
memory = MemorySaver()
# %%
llm = ChatOllama(model="gemma4:26b")
llm_with_tools = llm.bind_tools(tool_list)

# %%
sys_message = SystemMessage(
    content="You are a helpful assistant tasked with selecting and optionally combining arithmatic operations on scalars or vectors using the provided tools."
)


# Node
def assistant(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([sys_message] + state["messages"])]}


# Graph
builder = StateGraph(MessagesState)

# Define nodes: these do the work
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tool_list))

# Define edges: these determine how the control flow moves
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", "assistant")
react_graph = builder.compile(checkpointer=memory)
# %%


display(Image(react_graph.get_graph(xray=True).draw_mermaid_png()))

# %%
config: RunnableConfig = {"configurable": {"thread_id": "1"}}

complex_question_mesage: List[AnyMessage] = [HumanMessage(content=complex_question)]
complex_question_response = react_graph.invoke(
    {"messages": complex_question_mesage}, config
)
# %%
for m in complex_question_response["messages"]:
    m.pretty_print()
# %%
complex_question_followup_message: List[AnyMessage] = [
    HumanMessage(content=complex_question_followup)
]
complex_question_followup_response = react_graph.invoke(
    {"messages": complex_question_followup_message}, config
)
# %%

for m in complex_question_followup_response["messages"]:
    m.pretty_print()
# %%
