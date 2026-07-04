# %%
import random
from dataclasses import dataclass
from pprint import pprint
from typing import Literal, Optional, TypedDict

from IPython.display import Image, display
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel
from pydantic.functional_validators import field_validator


# %%
class TypedDictState(TypedDict):
    name: str
    mood: Optional[Literal["happy", "sad"]]


def node_1(state: TypedDictState):
    print("__Node 1__")
    return {"name": state["name"] + " is ..."}


def node_2(state: TypedDictState):
    print("__Node 2__")
    return {"mood": "happy"}


def node_3(state: TypedDictState):
    print("__Node 3__")
    return {"mood": "sad"}


def decide_mood(state: TypedDictState) -> Literal["node_2", "node_3"]:
    if random.random() < 0.5:
        return "node_2"
    else:
        return "node_3"


# %%

builder = StateGraph(TypedDictState)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", decide_mood)
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)
graph = builder.compile()

display(Image(graph.get_graph().draw_mermaid_png()))
# %%
initial_state = TypedDictState(name="test")
for i in range(10):
    result = graph.invoke(initial_state)
    print(result)
# %%


# %%
@dataclass
class DataclassState:
    name: str
    mood: Optional[Literal["happy", "sad"]]


initial_state_dc = DataclassState(name="test", mood=None)

builder_dc = StateGraph(DataclassState)
builder_dc.add_node("node_1", node_1)
builder_dc.add_node("node_2", node_2)
builder_dc.add_node("node_3", node_3)

builder_dc.add_edge(START, "node_1")
builder_dc.add_conditional_edges("node_1", decide_mood)
builder_dc.add_edge("node_2", END)
builder_dc.add_edge("node_3", END)
dc_graph = builder_dc.compile()
display(Image(dc_graph.get_graph().draw_mermaid_png()))
# %%

result_dc = dc_graph.invoke(initial_state_dc)

print(result_dc)
# %%


class PydanticState(BaseModel):
    name: str
    mood: Optional[Literal["happy", "sad"]]

    @field_validator("mood")
    @classmethod
    def validate_mood(cls, value):
        if value not in ["happy", "sad"]:
            raise ValueError("mood must be either happy or sad for validator")
        return value


# %%


def node_err(state: PydanticState):
    return {"mood": "mad"}


def decide_mood_with_error_prob(
    state: PydanticState,
) -> Literal["node_2", "node_3", "node_err"]:
    val = random.random()
    if val < 0.25:
        return "node_2"
    elif val < 0.5:
        return "node_3"
    else:
        return "node_err"


builder_pydantic = StateGraph(PydanticState)
builder_pydantic.add_node("node_1", node_1)
builder_pydantic.add_node("node_2", node_2)
builder_pydantic.add_node("node_3", node_3)
builder_pydantic.add_node("node_err", node_err)
builder_pydantic.add_edge(START, "node_1")
builder_pydantic.add_conditional_edges("node_1", decide_mood_with_error_prob)
builder_pydantic.add_edge("node_2", END)
builder_pydantic.add_edge("node_3", END)

pydantic_graph = builder_pydantic.compile()
display(Image(pydantic_graph.get_graph().draw_mermaid_png()))


# %%

initial_pydantic_val = PydanticState(name="test", mood=None)
initial_pydantic_val.name = "test"
for _ in range(10):
    result = pydantic_graph.invoke(initial_pydantic_val)
    pprint(result)
# %%
