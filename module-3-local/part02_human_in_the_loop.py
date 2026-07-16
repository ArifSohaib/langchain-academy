# %%
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, AnyMessage
from typing import Literal
from langgraph.checkpoint.memory import MemorySaver
from langgraph_sdk import get_client
from langgraph.graph import START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.state import StateGraph
from IPython.display import display, Image, Markdown
from simple_tools import add, multiply, divide, sub, pow, apply_to_list
# %%
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

memory = MemorySaver()
graph = builder.compile(checkpointer=memory,interrupt_before=["tools"])
display(Image(graph.get_graph().draw_mermaid_png()))
# %%

complex_question = """
complex_question = "While the total is less than 10,000 multiple the values in the list [102, 100, 200, 150, 101, 90, 101,100,110,110,] by 10 and keep adding. What does the total come out to BEFORE reaching 10,000. Use the provided tools.
"""
initial_input = [HumanMessage(content=complex_question)]
thread = RunnableConfig(configurable={"thread_id":"1"})
for event in graph.stream({"messages":initial_input},config=thread,stream_mode="values"):
    event['messages'][-1].pretty_print()
# %%
state = graph.get_state(thread)
print(state)
# %%
print(state.next)
# %%
for event in graph.stream(None, thread, stream_mode="values"):
    event["messages"][-1].pretty_print()

# %%
state = graph.get_state(thread)

print(state.next)
# %%
for event in graph.stream(None, thread, stream_mode="values"):
    event['messages'][-1].pretty_print()
# %%
initial_input2 = {"messages":HumanMessage(content="multiply 76 by 123")}
thread2 = RunnableConfig(configurable={"thread_id":"10"})
for event in graph.stream(initial_input2, thread2, stream_mode="values"):
    event['messages'][-1].pretty_print()
# %%
# run until first interruption. In the previous option we used None to skip instead of ask for approval
user_approval = input("do you want to call the tool? (yes/no)")
if user_approval.lower() == 'yes':
    for event in graph.stream(None, thread, stream_mode="values"):
        event['messages'][-1].pretty_print()
else:
    print("operation cancelled by user")
