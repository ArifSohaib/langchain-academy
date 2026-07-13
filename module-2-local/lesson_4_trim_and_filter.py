# %%

from pprint import pprint
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage, AnyMessage, RemoveMessage
from langgraph.graph import add_messages
from typing import List
from IPython.display import display, Image
from langgraph.graph import StateGraph, MessagesState, START,END
from langchain_core.messages import trim_messages
# %%
messages:List[AnyMessage] = [AIMessage(content="so you said you were researching langchain?", name="Bot")]
messages = add_messages(messages, [HumanMessage(content="yes, I need to know how to use schemas for filtering and trimming messages between graph nodes",name="Sohaib")])

for msg in messages:
    msg.pretty_print()
# %%
llm = ChatOllama(model="gemma4:e4b", temperature=0.1)
result_from_simple_llm = llm.invoke(messages)
# %%
messages = add_messages(messages, [result_from_simple_llm])
# %%
for msg in messages:
    msg.pretty_print()
# %%
def chat_model_node_simple(state:MessagesState):
    invoke_result = llm.invoke(state["messages"])
    return {"messages": add_messages(state['messages'], [invoke_result])}


simple_chat_builder = StateGraph(MessagesState)
simple_chat_builder.add_node("chat_node",chat_model_node_simple)
simple_chat_builder.add_edge(START, "chat_node")
simple_chat_builder.add_edge("chat_node", END)
simple_chat_graph = simple_chat_builder.compile()

# %%
messages_graph1:List[AnyMessage] = [AIMessage(content="so you said you were researching langchain?", name="Bot")]
messages_graph1 = add_messages(messages_graph1, [HumanMessage(content="yes, I need to know how to use schemas for filtering and trimming messages between graph nodes",name="Sohaib")])
simple_graph1_result = simple_chat_graph.invoke({"messages":messages_graph1})

# %%
pprint(simple_graph1_result)
# %%
for msg in simple_graph1_result['messages']:
    msg.pretty_print()
# %%
def delete_all_except_2_messages(state:MessagesState):
    """
    delete all except the last 2 messages
    """
    delete_messages = [RemoveMessage(id=msg.id) for msg in state['messages'][:-2]]
    return {"messages":delete_messages}
chat_with_delete_builder = StateGraph(MessagesState)
chat_with_delete_builder.add_node("chat_node",chat_model_node_simple)
chat_with_delete_builder.add_node("filter", delete_all_except_2_messages)
chat_with_delete_builder.add_edge(START, "chat_node")
chat_with_delete_builder.add_edge("chat_node", "filter")
chat_with_delete_builder.add_edge("filter", END)
chat_with_delete_graph = chat_with_delete_builder.compile()

# %%
display(Image(chat_with_delete_graph.get_graph().draw_mermaid_png()))
# %%
messages_graph2:List[AnyMessage] = [AIMessage(content="so you said you were researching langchain?", name="Bot")]
messages_graph2 = add_messages(messages_graph2, [HumanMessage(content="yes, I need to know how to use schemas for filtering and trimming messages between graph nodes",name="Sohaib")])
simple_graph1_result = simple_chat_graph.invoke({"messages":messages_graph2})
chat_with_delete_result = chat_with_delete_graph.invoke({"messages":messages_graph2})
# %%
for msg in chat_with_delete_result['messages']:
    msg.pretty_print()
# %%
trim_messages(chat_with_delete_result['messages'], max_tokens=100, strategy="last", token_counter=ChatOllama(model="gemma4:e4b"), allow_partial=False)
# %%
for msg in chat_with_delete_result['messages']:
    msg.pretty_print()
# %%
