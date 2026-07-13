# %%

from typing import TypedDict
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END
from pprint import pprint
class PrivateStateSimple(TypedDict):
    bar:int

class OverallStateSimple(TypedDict):
    foo:int

# %%


def node1(state:OverallStateSimple)->PrivateStateSimple:
    return {"bar":state['foo']+1}
def node2(state:PrivateStateSimple)->OverallStateSimple:
    return {"foo": state["bar"] + 1 }

graph_def_1 = StateGraph(OverallStateSimple)
graph_def_1.add_node("node1",node1)
graph_def_1.add_node("node2",node2)

graph_def_1.add_edge(START, "node1")
graph_def_1.add_edge("node1","node2")
graph_def_1.add_edge("node2", END)
graph1 = graph_def_1.compile()

# %%
display(Image(graph1.get_graph().draw_mermaid_png()))
# %%
result1 = graph1.invoke({"foo":0})
pprint(result1)


# %%
class OverallStateQuestion(TypedDict):
    name:str
    question: str
    answer: str
    notes: str

def thinking_node(state:OverallStateQuestion):
    return {"answer":"bye", "notes":f"---his name is {state['name']}"}
def answer_node(state:OverallStateQuestion):
    return {"answer":f"bye {state['name']}"}

thinking_node_build = StateGraph(OverallStateQuestion)
thinking_node_build.add_node("thinking_node",thinking_node)
thinking_node_build.add_node("answer_node",answer_node)
thinking_node_build.add_edge(START, "thinking_node")
thinking_node_build.add_edge("thinking_node","answer_node")
thinking_node_build.add_edge("answer_node", END)
thinking_graph = thinking_node_build.compile()
# %%
display(Image(thinking_graph.get_graph().draw_mermaid_png()))
# %%
thinking_graph_response = thinking_graph.invoke({"name":"Sohaib", "question":"test question"})
# %%
pprint(thinking_graph_response)
# %%
class InputStateSplit(TypedDict):
    question:str
class OutputStateSplit(TypedDict):
    answer: str
class OverallStateSplit(TypedDict):
    question: str
    answer: str
    notes: str
# %%
def thinking_node_split(state:InputStateSplit)->OverallStateSplit:
    return {"question":state["question"], "answer":"bye", "notes":"--found some notes"}
def answer_node_split(state:OverallStateSplit)->OutputStateSplit:
    return {"answer": state['answer']}
# %%
split_graph_build = StateGraph(OverallStateSplit)
split_graph_build.add_node("question_node",thinking_node_split)
split_graph_build.add_node("answer_node",answer_node_split)
split_graph_build.add_edge(START, "question_node")
split_graph_build.add_edge("question_node","answer_node")
split_graph_build.add_edge("answer_node", END)
split_graph = split_graph_build.compile()
# %%
display(Image(split_graph.get_graph().draw_mermaid_png()))
# %%
split_graph_result = split_graph.invoke({"question":"test"})

# %%
pprint(split_graph_result)
# %%
