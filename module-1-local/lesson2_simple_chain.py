# %%
import random
from typing import Literal, TypedDict

from IPython.display import Image, display
from langgraph.graph import END, START, StateGraph

# %%


class State(TypedDict):
    graph_state: str


def node_1(state):
    print("__Node 1__")
    return {"graph_state": state["graph_state"] + "\nI am"}


def node_2(state):
    print("__Node 2__")
    return {"graph_state": f"{state['graph_state']} happy!"}


def node_3(state):
    print("__Node 3__")
    return {"graph_state": f"{state['graph_state']} sad!"}


# %%


def decide_mood(state) -> Literal["node_2", "node_3"]:
    user_input = state["graph_state"]
    print(f"user_input:{user_input}")
    if random.random() < 0.5:
        return "node_2"
    return "node_3"


# %%

builder = StateGraph(State)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", decide_mood)
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

# %%
graph = builder.compile()

# %%
display(Image(graph.get_graph().draw_mermaid_png()))
# %%
# graph.invoke("hello") #will not work because it needs a "graph_state"
graph.invoke({"graph_state": "Hi, this is Sohaib\n"})
# %%
