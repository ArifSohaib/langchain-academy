# %%
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, AnyMessage
from typing import Literal
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.state import StateGraph
from IPython.display import display, Image, Markdown
# %%
#simple tools
def multiply(a:float|int, b:float|int)->float|int:
    """
    Add a and b
    returns:
        float or int
    """
    return a * b

def divide(a:float|int, b:float|int)->float|int:
    """
    divides a by b
    Args:
        a: int or float
        b: int or float
    Returns:
        a divided by b
    """
    return a / b


def add(a:float|int, b:float|int)->float|int:
    """
    add a and b
    Args:
        a: int or float
        b: int or float
    Returns:
        a + b
    """
    return a + b


def sub(a:float|int, b:float|int)->float|int:
    """
    subtracts a and b
    Args:
        a: int or float
        b: int or float
    Returns:
        a - b
    """
    return a -  b

def pow(a:float|int, b:float|int)->float|int:
    """
    subtracts a and b
    Args:
        a: int or float
        b: int or float
    Returns:
        a to the power of  b
    """
    return a **  b

def apply_to_list(a:list[float|int], op:str, operand:float|int)->list[float|int]|str:
    """
    applies a function to a list
    Args:
        a: list of ints or floats
        b: list of ints or floats
        op: the function to apply
        operand": the value to apply
    Returns:
        list of floats or ints after applying operation
    """
    available_ops:dict[str, func] = {
        "add":add,
        "mul":multiply,
        "divide":divide,
        "sub":sub,
        "pow":pow
    }
    if op in available_ops:
        return  [available_ops[op](x, operand) for x in a]
    else:
        return "operator not found"
# %%
llm = ChatOllama(model="gemma4:e4b")
tools = [add,multiply, divide, sub, pow, apply_to_list]

llm_with_tools = llm.bind_tools(tools)

sys_message = SystemMessage(content="you are a helpful assistant used to perform scalar and vector math on sets of inputs")
def assistant(state:MessagesState):
    return {"messages":[llm_with_tools.invoke([sys_message]+state["messages"])]}

builder = StateGraph(MessagesState)
builder.add_node("assistant",assistant)
builder.add_node("tools",ToolNode(tools))
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant",tools_condition)
builder.add_edge("tools","assistant")

memory = MemorySaver()
graph = builder.compile(checkpointer=memory,interrupt_before=["tools"])
display(Image(graph.get_graph().draw_mermaid_png()))
# %%
initial_input = [HumanMessage(content="multiply 1123 by 34")]
thread = RunnableConfig(configurable={"thread_id":"1"})
for event in graph.stream({"messages":initial_input},config=thread,stream_mode="values"):
    event['messages'][-1].pretty_print()
# %%
state = graph.get_state(thread)
print(state)
# %%
print(state.next)
# %%
