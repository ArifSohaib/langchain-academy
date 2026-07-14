"""
adding streamlit based ui to previous load and resume code
I know this can be made more modular but the point right now is to just add two additions to the presistance part from the course
"""
#%%
from langchain_core.messages.ai import AIMessage
import streamlit as st
import sqlite3
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END, START
from langchain.messages import RemoveMessage, SystemMessage, HumanMessage
from typing import  Literal
from langgraph.graph import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import MessagesState
from langgraph.graph.state import CompiledStateGraph
from pathlib import Path
from langchain_core.runnables import RunnableConfig
# %%
db_path = Path("state_db","example.db")
conn = sqlite3.connect(str(db_path), check_same_thread=False)
# %%
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
# %%
config = RunnableConfig(configurable={"thread_id":"1"}) # TODO: allow user to select thread id
# %%
state_so_far = graph.get_state(config)
summary_so_far = state_so_far.values['summary']
messages_so_far = state_so_far.values['messages']

st.session_state['messages'] = messages_so_far
st.session_state['summary'] = summary_so_far
# %%
def invoke_and_append_message(graph:CompiledStateGraph,config:RunnableConfig, message:str):
    graph_state = graph.get_state(config)
    messages = graph_state.values['messages']
    summary = graph_state.values['summary']
    messages = add_messages(messages, [HumanMessage(content=message)])
    new_state = SummaryState(messages=messages, summary=summary)
    new_response = graph.invoke(input=new_state, config=config)
    return new_response
# %%
if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    if isinstance(message, AIMessage):
        role = "ai"
    else:
        role = "user"
    with st.chat_message(role):
        st.markdown(message.content)

if prompt := st.chat_input("follow up or new question"):
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    response = invoke_and_append_message(graph, config, prompt)
    with st.chat_message("ai"):
        response_text = response['messages'][-1]
        st.markdown(response_text)
