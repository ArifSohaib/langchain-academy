
# %%
from langgraph.graph import MessagesState, START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.errors import NodeInterrupt
from typing import TypedDict
from IPython.display import display, Image
from langgraph.pregel.protocol import RunnableConfig
# %%
class State(TypedDict):
    input: str

def step_1(state:State):
    print("__step 1__")
    return state
# %%
def step_2(state:State):
    print("__step 2__")
    if len(state['input'])>5:
        raise NodeInterrupt(f"recieved input that is larger than 5 chars")
    return state
# %%
def step_3(state:State):
    print("__state 3__")
    return state
# %%
interruptable_builder  = StateGraph(State)
interruptable_builder.add_node("node_1", step_1)
interruptable_builder.add_node("node_2", step_2)
interruptable_builder.add_node("node_3", step_3)

interruptable_builder.add_edge(START, "node_1")
interruptable_builder.add_edge("node_1", "node_2")
interruptable_builder.add_edge("node_2", "node_3")
interruptable_builder.add_edge("node_3", END)
memory = MemorySaver()
interruptable_graph = interruptable_builder.compile(checkpointer=memory)

display(Image(interruptable_graph.get_graph().draw_mermaid_png()))
# %%

thread = RunnableConfig(configurable={"thread_id":"5"})
result = interruptable_graph.invoke({"input":"hello world"}, thread)
# %%
print(result)
# %%
thread2 = RunnableConfig(configurable={"thread_id":"1"})

for event in interruptable_graph.stream({"input":"test input"}, thread2, stream_mode="values"):
    print(event['input'][-1])
# %%
state = interruptable_graph.get_state(thread2)
print(state.tasks)

# %%
new_state = interruptable_graph.update_state(thread2, {"input":"H1"})
for event in interruptable_graph.stream({"input":"hi"}, thread2, stream_mode="values"):
    print(event['input'][-1])

# %%
all_states = [s for s in interruptable_graph.get_state_history(thread2)]
print(len(all_states))

# %%
print(all_states[-1])
# %%
print(all_states[-2].config['configurable']['checkpoint_id'])
print(all_states[-2].values['input'])

# %%
