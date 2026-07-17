"""
allowing human editing of input
"""
# %%
from langchain.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph
from simple_tools import add, sub, multiply, divide, apply_to_list
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph,  START, MessagesState
from pathlib import Path
from pprint import pprint
from IPython.display import display, Image
# %%
tools = [add, sub, multiply, divide, apply_to_list]
llm = ChatOllama(model="gemma4:e4b", temperature=0.1)
llm_with_tools = llm.bind_tools(tools)
# %%
sys_msg = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")
def assistant(state: MessagesState):
   return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

# %%

builder = StateGraph(MessagesState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant",tools_condition)
builder.add_edge("tools", "assistant")
# %%
state_db = Path("state_db","input_edit.db")
conn = sqlite3.connect(str(state_db),check_same_thread=False)
memory_sql = SqliteSaver(conn)
memory = MemorySaver()

# pausing before assistant and not before tools, this way the input to tools can be edited before running
graph = builder.compile(interrupt_before=["assistant"], checkpointer=memory)
# %%
display(Image(graph.get_graph().draw_mermaid_png()))
# %%


def call_graph(message:str, graph:CompiledStateGraph, thread:RunnableConfig):
    new_input = [HumanMessage(content=message)]
    for event in graph.stream({"messages":new_input}, config=thread, stream_mode="values"):
        event['messages'][-1].pretty_print()
# %%

thread = RunnableConfig(configurable={"thread_id":"1"})
call_graph("multiply 34 by 346 ", graph, thread)
# %%
new_state = graph.get_state(thread)
# %%
pprint(new_state.values['messages'])
# %%

def go_to_next(graph:CompiledStateGraph, thread:RunnableConfig):
    for event in graph.stream(None, config=thread, stream_mode="values"):
        event['messages'][-1].pretty_print()
# %%
go_to_next(graph, thread)
# %%
## running with interrupt + state edit
thread2 = RunnableConfig(configurable={"thread_id":"10"})
msg = "multiply the list [1,3,5,7,8,10] by 100 then add the result back to the list"
call_graph(msg, graph,thread2 )
# %%
new_config = graph.update_state(thread2, {"messages":[HumanMessage(content="no actually change the list to [1,3,5,7,9,11] multiply it by 100 and add the result back to the list")]})
# %%

state_after_update = graph.get_state(new_config)
# %%
for msg in  state_after_update.values['messages']:
    msg.pretty_print()
# %%
pprint(state_after_update.next)
# %%
go_to_next(graph,new_config)
# %%
go_to_next(graph,new_config)
# %%
