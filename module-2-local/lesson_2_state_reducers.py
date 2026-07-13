# %%
from operator import add
from pprint import pprint
from typing import List

from IPython.display import Image, display
from langgraph.graph import END, START, StateGraph
from typing_extensions import Annotated, TypedDict
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langgraph.graph.message import MessagesState, add_messages
from langchain_core.messages import RemoveMessage
from typing import Literal
# What problem the reducer solves
# simple state and state update

# %%
class State(TypedDict):
    foo: int

def node_1(state: State):
    print("__node 1__")
    return {
        "foo": state["foo"] + 1,
    }

def node_2(state:State):
    print("__node 2__")
    return {"foo": state["foo"] + 1}

def node_3(state:State):
    print("__node 3__")
    return {"foo": state["foo"] + 1}
# %%

graph_def = StateGraph(State)
graph_def.add_node("node_1",node_1)
graph_def.add_node("node_2",node_2)
graph_def.add_node("node_3",node_3)

graph_def.add_edge(START, "node_1")
graph_def.add_edge("node_1", "node_2")
graph_def.add_edge("node_1", "node_3")
graph_def.add_edge("node_2", END)
graph_def.add_edge("node_3", END)

graph = graph_def.compile()

# %%
display(Image(graph.get_graph().draw_mermaid_png()))

# %%
## Problem with above graph is that node_2 and node_3 are called simultaneously and both update the state of foo together
graph.invoke({"foo":1})
## To fix above issue we use annotated state with add operation on foo
# Reducers tell how to update a key explicitly. Without defining explicit reducers, each update just overrides the pervious one which also means simultanous updates like above can not happen
# documentation for reducers https://docs.langchain.com/oss/python/langgraph/graph-api/#reducers
#
# %%
class StateWithReducer(TypedDict):
    foo: Annotated[List[int], add]

def node_1_reducer(state:StateWithReducer):
    print("__node 1__")
    return {"foo": [state['foo'][0] + 1]}

def node_2_reducer(state:StateWithReducer):
    print("__node 2__")
    return {"foo": [state['foo'][0] + 1]}

def node_3_reducer(state:StateWithReducer):
    print("__node 3__")
    return {"foo": [state['foo'][0] + 1]}

graph_def_reducer = StateGraph(StateWithReducer)
graph_def_reducer.add_node("node_1",node_1_reducer)
graph_def_reducer.add_node("node_2",node_2_reducer)
graph_def_reducer.add_node("node_3",node_3_reducer)

graph_def_reducer.add_edge(START,"node_1")

graph_def_reducer.add_edge("node_1","node_2")
graph_def_reducer.add_edge("node_1","node_3")
graph_def_reducer.add_edge("node_2",END)
graph_def_reducer.add_edge("node_3",END)

graph_with_reducer = graph_def_reducer.compile()

display(Image(graph_with_reducer.get_graph().draw_mermaid_png()))

# %%
reducer_1_result = graph_with_reducer.invoke({"foo":[1]})
# %%
pprint(reducer_1_result)
# %%
reducer_1_result2 = graph_with_reducer.invoke({"foo":[1,2,3]})
pprint(reducer_1_result2)
## Note that each of the three nodes append one value which is 1 added to the value at index 0 so for both above cases it is adding 2 at node 1, 2 at node 2 and 2 again at node 3
# %%
def node1_reducer2(state:StateWithReducer):
    print("__node1__")
    return {"foo":[state['foo'][-1]+1]}

def node2_reducer2(state:StateWithReducer):
    print("__node2__")
    return {"foo":[state['foo'][-1]+1]}

def node3_reducer2(state:StateWithReducer):
    print("__node3__")
    return {"foo":[state['foo'][-1]+1]}
graph_def_reducer2 = StateGraph(StateWithReducer)
graph_def_reducer2.add_node("node_1",node1_reducer2)
graph_def_reducer2.add_node("node_2",node2_reducer2)
graph_def_reducer2.add_node("node_3",node3_reducer2)

graph_def_reducer2.add_edge(START,"node_1")

graph_def_reducer2.add_edge("node_1","node_2")
graph_def_reducer2.add_edge("node_1","node_3")
graph_def_reducer2.add_edge("node_2",END)
graph_def_reducer2.add_edge("node_3",END)

graph_with_reducer2 = graph_def_reducer2.compile()
# %%
display(Image(graph_with_reducer2.get_graph().draw_mermaid_png()))
# %%
reducer_2_result1 = graph_with_reducer2.invoke({"foo":[0]})
pprint(reducer_2_result1)
#notice in the above result that 1 was added to the initial value of the list in foo, then 1 was added to that result twice because the state at foo[-1] when node 2 and node 3 are called is the same
# %%
reducer_2_result2 = graph_with_reducer2.invoke(reducer_2_result1)
# %%
pprint(reducer_2_result2)
# When called on the result of the previous call invoke, 1 is added to the last value (2) and then twice to the resulting value
# %%
## Custom Redeucers
#  with the above graph if we invoke with an empty list it will not find the value at -1
#  if we call the above with a None in foo, a similar issue will happen
# to handle these cases we can use custom reducers
# %%
try:
    reducer_2_result_empty = graph_with_reducer2.invoke({"foo":[]})
    pprint(reducer_2_result_empty)
except Exception as ex:
    print(f"{ex=}")
# %%
try:
    reducer_2_result_none = graph_with_reducer2.invoke({"foo":None})
    pprint(reducer_2_result_none)
except Exception as ex:
    print(f"{ex=}")
# %%
def reduce_list(left:List[int]|None, right:List[int]|None)->List[int]:
    """
    Safely combine two lists handling cases where one or both may be null
    """
    if not left:
        left = []
    if not right:
        right = []
    return left+right
class CustomReducer(TypedDict):
    foo: Annotated[List[int], reduce_list]

def node_1_custom(state:CustomReducer):
    print("__node_1__")
    return {"foo":[1]}

graph_def_custom_reducer = StateGraph(CustomReducer)
graph_def_custom_reducer.add_node("node_1",node_1_custom)
graph_def_custom_reducer.add_edge(START,"node_1")
graph_def_custom_reducer.add_edge("node_1",END)

graph_custom_reducer = graph_def_custom_reducer.compile()
display(Image(graph_custom_reducer.get_graph().draw_mermaid_png()))
# %%
custom_reducer_result1 = graph_custom_reducer.invoke({"foo":[]})
pprint(f"{custom_reducer_result1=}")
custom_reducer_result = graph_custom_reducer.invoke({"foo":None})
for _ in range(5):
    custom_reducer_result = graph_custom_reducer.invoke(custom_reducer_result)
    pprint(custom_reducer_result)
# %%
# MessagesState have their own built in reducers
# In this case we start with MessagesState directly so no need to define class
#
def message_state_node1(state:MessagesState):
    return {"messages":add_messages(state["messages"], [AIMessage("new message added")])}

message_state_graph_def = StateGraph(MessagesState)
message_state_graph_def.add_node("node_1",message_state_node1)
message_state_graph_def.add_edge(START, "node_1")
message_state_graph_def.add_edge("node_1",END)

message_state_graph = message_state_graph_def.compile()
message_state_graph_result = message_state_graph.invoke({"messages":[AIMessage(content="hello how can i help you?"),HumanMessage(content='initial message')]})
pprint(message_state_graph_result)

# %%
for msg in message_state_graph_result['messages']:
    print(f"{msg.id=}")
    msg.pretty_print()
# %%
def message_state_erase_last_node(state:MessagesState):
    if len(state['messages']) == 0:
        return {"messages":AIMessage(content="no message to delete")}
    last_messages = state['messages'][:-2]
    print("deleting message")
    [RemoveMessage(id=m.id) for m in last_messages]


def erase_message_cond(state:MessagesState)->Literal["node_2", "remove_msg"]:
    if state["messages"][-1].content == "delete last node":
        return "remove_msg"
    else:
        return "node_2"


def message_state_node2(state:MessagesState):
    return {"messages":add_messages(state["messages"], [AIMessage("new message added from second node")])}


message_state_graph_def2 = StateGraph(MessagesState)
message_state_graph_def2.add_node("node_1",message_state_node1)
message_state_graph_def2.add_node("node_2",message_state_node2)
message_state_graph_def2.add_node("remove_msg",message_state_erase_last_node)
message_state_graph_def2.add_edge(START, "node_1")
message_state_graph_def2.add_conditional_edges("node_1", erase_message_cond)
message_state_graph_def2.add_edge("node_2",END)

message_state_graph2 = message_state_graph_def2.compile()

display(Image(message_state_graph2.get_graph().draw_mermaid_png()))

# %%
message_state_graph2_result = message_state_graph2.invoke({"messages":[AIMessage(content="hello how can i help you?"),HumanMessage(content='initial message')]})
pprint(message_state_graph2_result)

# %%
add_messages(message_state_graph2_result['messages'], AIMessage(content="delete last node"))
# %%
message_state_graph2_result2 = message_state_graph2.invoke(message_state_graph2_result)
for msg in message_state_graph2_result2['messages']:
    msg.pretty_print()
# %%
