"""
using the dynamic breakpoints to "time travel" to previous points in conversation
"""
# %%
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState, START, StateGraph
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langchain.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.prebuilt import tools_condition, ToolNode
from simple_tools import add, sub, multiply, divide, pow, apply_to_list, split_string, convert_string_to_ord
from IPython.display import display, Image

# %%
tools = [add, sub, multiply,divide, pow, apply_to_list, split_string, convert_string_to_ord]
llm = ChatOllama(model="gemma4:e4b", temperature=0.1)
llm_with_tools = llm.bind_tools(tools)
# %%
print(llm.temperature)
# %%

def assistant(state:MessagesState):
    sys_message = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs. You can use multiply tool calls for the same problem.")
    result = llm_with_tools.invoke([sys_message] + state["messages"])
    return {"messages":result}
# %%
builder = StateGraph(MessagesState)
builder.add_node("assistant",assistant)
builder.add_node("tools",ToolNode(tools))
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant",tools_condition)
builder.add_edge("tools", "assistant")
memory = MemorySaver()
graph = builder.compile(checkpointer=memory, interrupt_before=["assistant"])
# %%

display(Image(graph.get_graph().draw_mermaid_png()))
# %%
simple_question1 = HumanMessage(content="multiply 2.5 by the list [3,1,4,6,7,1,7] then divide the result by 2 and sum over the list")
thread1 = RunnableConfig(configurable={"thread_id":"1"})
for event in graph.stream({"messages":[simple_question1]}, config=thread1, stream_mode="values"):
    event['messages'][-1].pretty_print()
# %%
for event in graph.stream(None, config=thread1,  stream_mode="values"):
    event['messages'][-1].pretty_print()

# %%
state_history1 = [h for h in graph.get_state_history(thread1)]
print(state_history1)
# %%
# get the snapshot id to reply
to_fork = state_history1[-2]
# %%
print(to_fork.config)
# %%
to_fork.values['messages'][-1].pretty_print()
# %%
#split from this checkpoint id
#same as original question by removing the final sum
fork_config = graph.update_state(to_fork.config,
    {"messages":[HumanMessage(
    content="multiply 2.5 by 2",
        id=to_fork.values["messages"][-1].id
)]})

# %%
for event in graph.stream(None, fork_config, stream_mode="values"):
    event['messages'][-1].pretty_print()

# %%
for event in graph.stream(None, {"configurable":{"thread_id":"1"}}, stream_mode="values"):
    event['messages'][-1].pretty_print()
# %%

for event in graph.stream(None, fork_config, stream_mode="values"):
    event['messages'][-1].pretty_print()
# %%
#move forward from original fork
print(to_fork.config)
# %%
#resuming from previous breakpoint
prev_event = None
for event in graph.stream(None, to_fork.config, stream_mode="values"):
    prev_event = event
    event['messages'][-1].pretty_print()

# %%
# since this was a complex question with multiple tool calls, it will need to be resumed multiple times before it gets an AIMessage output
while prev_event and isinstance(prev_event,dict) and not isinstance(prev_event['messages'][-1],AIMessage) and prev_event['messages'][-1].content != '':
    #note the configurable here it is not using the to_fork.config because that ends at a specific checkpoint, for the multi-tool call
    # idea, we need to stream the next value after that chcekpoint was run
    for event in graph.stream(None, {"configurable":{"thread_id":"1"}}, stream_mode="values"):
        prev_event = event
        event['messages'][-1].pretty_print()

# %%
