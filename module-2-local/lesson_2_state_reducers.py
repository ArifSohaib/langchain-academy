# %%
from operator import add
from pprint import pprint
from typing import List

from IPython.display import Image, display
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from typing_extensions import Annotated, Literal, TypedDict


# %%
class State(TypedDict):
    foo: int
    bar: int
    messages: Annotated[List[AnyMessage], add]


def node_1(state: State):
    print("__node 1__")
    return {
        "foo": state["foo"] + 1,
        "messages": state["messages"] + [AIMessage(content="called")],
    }


def node_2(state: State):
    print("__node 2__")
    return {
        "foo": state["foo"] + 1,
        "messages": state["messages"] + [AIMessage(content="called from ai")],
    }


def node_3(state: State):
    print("__node 2__")
    return {
        "bar": state["bar"] + 1,
        "messages": state["messages"] + [HumanMessage(content="called from human")],
    }


def next_turn(state: State) -> Literal["node_3", "node_2"]:
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage):
        return "node_3"
    else:
        return "node_2"


# %%
builder = StateGraph(State)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)
builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", next_turn)
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)
graph = builder.compile()
display(Image(graph.get_graph().draw_mermaid_png()))

# %%
initial_state = State(foo=0, bar=0, messages=[HumanMessage(content="test")])


result = graph.invoke(initial_state)
pprint(f"{result=},{type(result)=}")
for m in result["messages"]:
    m.pretty_print()

# %%
