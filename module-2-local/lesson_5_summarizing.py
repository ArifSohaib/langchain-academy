# %%

from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage, RemoveMessage
from langgraph.graph.message import MessagesState
from typing import Literal, List
from langgraph.graph import add_messages
from langgraph.checkpoint.memory import MemorySaver
from IPython.display import display, Image, Markdown
# %%

model = ChatOllama(model="gemma4:e4b")

class SummaryState(MessagesState):
    summary: str

def call_model(state:SummaryState):
    summary = state.get("summary", "")
    if summary:
        system_message = f"Summary of conversation earlier: {summary}"
        messages = add_messages([SystemMessage(content=system_message)], state.get("messages","") )
    else:
        messages = state['messages']
    print(f"{messages=} in call model")
    response = model.invoke(messages)
    messages = add_messages(messages, [response])
    return {"messages":messages}

def summarize_conversation(state:SummaryState):
    summary = state.get("summary", "")
    if summary:
        summary_message = f"This is a summary of the conversation to date: {summary}\n\n Extend this summary by taking into account the new messages above"
    else:
        summary_message = "create a summary of the conversdation above"
    messages = add_messages(state["messages"], [HumanMessage(content=summary_message)])
    response = model.invoke(messages)
    delete_messages = [RemoveMessage(msg.id) for msg in messages[:-2]]
    return {"summary":response.content, "messages":delete_messages}

def should_continue(state:SummaryState)->Literal["summary", END]:
    messages = state['messages']
    if len(messages)>3:
        return "summary"
    else:
        return END
# %%
summary_graph_builder = StateGraph(SummaryState)
summary_graph_builder.add_node("conversation", call_model)
summary_graph_builder.add_node("summary", summarize_conversation)
summary_graph_builder.add_edge(START, "conversation")
summary_graph_builder.add_conditional_edges("conversation", should_continue)
summary_graph_builder.add_edge("conversation", END)

memory = MemorySaver()
summary_graph = summary_graph_builder.compile(checkpointer=memory)
display(Image(summary_graph.get_graph().draw_mermaid_png()))

# %%
# Create a thread
config = {"configurable": {"thread_id": "1"}}
messages_so_far:List[AnyMessage] = [HumanMessage(content="can you help me understand ways to use memory and summarize conversations using langgraph")]
messages_state = SummaryState(messages=messages_so_far,summary="")
# %%
result = summary_graph.invoke(input=messages_state, config=config)
# %%


# %%
for msg in result['messages']:
    msg.pretty_print()
# %%
messages_so_far_ = add_messages(result['messages'],
    [HumanMessage(content=
        "What are some changes or differences between presistant memory via a local db vs using MemorySaver from langgraph.checkpoint.memory")])
# %%
messages_state = SummaryState(messages=messages_so_far_,summary="")
# %%
result = summary_graph.invoke(input=messages_state, config=config)
# %%
for msg in result['messages']:
    msg.pretty_print()


# %%

messages_so_far_ = add_messages(result['messages'],
    [HumanMessage(content="Can I use duckdb or sqlite?")])
messages_so_far = SummaryState(messages=messages_so_far_, summary="")
result = summary_graph.invoke(input={"messages":next_question}, config=config)

# %%

display(Markdown(result['summary']))
# %%
