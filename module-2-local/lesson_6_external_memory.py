# %%
import sqlite3
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END, START
from langchain.messages import AnyMessage, RemoveMessage, SystemMessage, HumanMessage, AIMessage
from typing import List, Literal
from langgraph.graph import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import MessagesState
from pathlib import Path
from langchain_core.runnables import RunnableConfig
from IPython.display import display, Image
from pprint import pprint

from pandas.io.formats.printing import Any
# %%

#conn = sqlite3.connect(":memory",) #in memory sqlite
db_path = Path("state_db","example.db")
conn = sqlite3.connect(str(db_path), check_same_thread=False)


model = ChatOllama(model="gemma4:e4b", temperature=0.1)
# %%
class SummaryState(MessagesState):
    summary:str

def call_model(state:SummaryState):
    summary = state.get("summary","")
    if summary:
        system_message = f"Summary of conversation earlier: {summary}"
        messages = add_messages([SystemMessage(content=system_message)],state["messages"])
    else:
        messages = state['messages']
    response = model.invoke(messages)
    messages = add_messages(messages, [response])
    return {"messages":messages}

def summarize_conversation(state:SummaryState):
    summary = state.get("summary","")
    if summary:
        summary_message = (f"This is summary of the conversation to date: {summary}\n\nExtend the summary by taking into account the new messages above:")
    else:
        summary_message = "Create a summary of the conversation above:"
    messages = add_messages(state["messages"],[HumanMessage(content=summary_message)])
    response = model.invoke(messages)
    delete_messages = [RemoveMessage(id=m.id) for m in messages[:-2]]
    return {"summary":response.content, "messages":delete_messages}

def should_continue(state:SummaryState)->Literal["summarize", END]:
    messages = state['messages']
    if len(messages) > 3:
        return "summarize"
    else:
        return END
# %%
workflow = StateGraph(SummaryState)
workflow.add_node("conversation", call_model)
workflow.add_node("summarize",summarize_conversation)
workflow.add_edge(START, "conversation")
workflow.add_conditional_edges("conversation", should_continue)
workflow.add_edge("conversation",END)
memory = SqliteSaver(conn)
graph = workflow.compile(checkpointer=memory)
display(Image(graph.get_graph().draw_mermaid_png()))

# %%

config = RunnableConfig(configurable={"thread_id":"1"})
# %%
graph_state = graph.get_state(config)
pprint(graph_state)
# %%
first_message:List[AnyMessage] = [HumanMessage(content="can you help me understand ways to use memory and summarize conversations using langgraph")]
state = SummaryState(messages=first_message, summary="")
# %%
result = graph.invoke(input=state, config=config )
# %%
messages_so_far = add_messages(first_message, result['messages'])
# %%
for msg in messages_so_far:
    msg.pretty_print()
# %%
second_message:List[AnyMessage] = [HumanMessage(content="what is the difference between inmemory saver, postgres and sqlite savers")]
messages_so_far = add_messages(messages_so_far, second_message)
new_state = SummaryState(messags=messages_so_far, summary="")
# %%
result2 = graph.invoke(input=new_state, config=config)
# %%
messages_so_far = add_messages(messages_so_far, result2['messages'])
# %%
for msg in messages_so_far:
    msg.pretty_print()

# %%

graph_state2 = graph.get_state(config=config)
# %%
pprint(graph_state2.values.keys())
# %%
for msg in graph_state2.values['messages']:
    msg.pretty_print()
# %%
