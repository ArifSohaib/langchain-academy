# %%
from IPython.display import display, Image
from typing import Literal
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage, AnyMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.memory import MemorySaver
from pathlib import Path
import sqlite3
from pprint import pprint

from langgraph.pregel.main import Runnable

# %%
model = ChatOllama(model="gemma4:e4b")
db_path = Path("state_db","example.db")
conn = sqlite3.connect(str(db_path), check_same_thread=False)
memory = SqliteSaver(conn)
# %%
class SummaryState(MessagesState):
    summary: str

def call_model(state:SummaryState, config: RunnableConfig):
    summary = state.get("summary","")
    if summary:
        system_message = f"Summary of conversation earlier: {summary}"

        #note: using + instead of add_message reducer because the reducer is already implemented internally
        messages = [SystemMessage(content=system_message)] + state["messages"]
    else:
        messages = state["messages"]

    result = model.invoke(messages ,config=config)

    return {"messages":result}

def summarize_conversation(state:SummaryState,config:RunnableConfig):
    summary=state.get("summary","")
    if summary:
        summary_message = (
                    f"This is summary of the conversation to date: {summary}\n\n"
                    "Extend the summary by taking into account the new messages above:"
        )
    else:
        summary_message = "Create a summary of the conversation above:"
    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = model.invoke(messages, config)
    delete_messages = [RemoveMessage(id=m.id) for m in state['messages'][:-2]]
    return {"summary":response.content, "messages":delete_messages}


def should_continue(state:SummaryState)->Literal["summarize_messages", END]:
    messages = state['messages']
    if len(messages) > 6:
        return "summarize_messages"
    else:
        return END
# %%

builder = StateGraph(SummaryState)
builder.add_node("conversation", call_model)
builder.add_node("summarize_messages", summarize_conversation)
builder.add_edge(START,"conversation")
builder.add_conditional_edges("conversation",should_continue)
#"conversation" already has an edge to END via should_continue
builder.add_edge("summarize_messages",END)

graph = builder.compile(checkpointer=memory)

# %%
display(Image(graph.get_graph().draw_mermaid_png()))
# %%

config = RunnableConfig(configurable={"thread_id":"1"})
initial_state = SummaryState(messages=[HumanMessage(content="testing graph")], summary="")

# %%
def stream_messages(config:RunnableConfig, message:str, stream_type:Literal['updates','values']):
    curr_state = graph.get_state(config)
    curr_summary = curr_state.values.get('summary','')
    curr_messages = curr_state.values.get('messages',[])
    new_state = SummaryState(messages=curr_messages+[HumanMessage(content=message)], summary=curr_summary)
    if stream_type == "values":
        for event in graph.stream(new_state, config=config, stream_mode=stream_type):
            for m in event['messages']:
                m.pretty_print()
    else:
        for chunk in graph.stream(new_state, config=config, stream_mode=stream_type):
            chunk['conversation']['messages'].pretty_printt()
# %%
config1 = RunnableConfig(configurable={"thread_id":"2"})
stream_messages(config1, message="I am trying to learn how to use streaming with langgraph",stream_type="values")
# %%
config1 = RunnableConfig(configurable={"thread_id":"3"})
stream_messages(config1, message="I am trying to learn how to use streaming with langgraph",stream_type="values")
# %%
memory_async = MemorySaver()
async_graph = builder.compile(memory_async)
config_async = RunnableConfig(configurable={"thread_id":"4"})
input_message_async = HumanMessage(content="I am trying to test out streaming with async langchain. How can I do that?")
async for event in async_graph.astream_events({"messages":[input_message_async]}, config=config_async, version='v2'):
    print(f"Node: {event['metadata'].get('langgraph_node','')}\n\n{event['event']}\n\n{event['name']}")
# %%
node_to_stream = "conversation"
config_async2 = RunnableConfig(configurable={"thread_id":"5"})
input_message_async2 = [HumanMessage(content="how can I select a node to stream data from in langgraph async streaming graph")]
async for event in async_graph.astream_events({"messages":input_message_async2},config=config_async2, version="v2"):
    if event['event'] == "on_chat_model_stream" and event["metadata"].get("langgraph_node","") == node_to_stream:
        pprint(event['data'])


# %%
node_to_stream = "conversation"
config_async3 = RunnableConfig(configurable={"thread_id":"6"})
input_message_async3:list[AnyMessage] = [HumanMessage(content="how can I select a node to stream data from in langgraph async streaming graph")]
async for event in async_graph.astream_events(SummaryState(messages=input_message_async3, summary=""),config=config_async3, version="v2"):
    if event['event'] == "on_chat_model_stream" and event["metadata"].get("langgraph_node","") == node_to_stream:
        data = event['data']
        print(data['chunk'].content, end="|")

# %%
