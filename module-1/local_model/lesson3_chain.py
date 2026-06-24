# %%
from functools import reduce
from pprint import pprint
from typing import List

import streamlit as st
from langchain_core.callbacks.manager import Func
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_ollama import ChatOllama
from langgraph.graph.message import AnyMessage
from typing_extensions import Callable

# %%
messages: List[AIMessage | HumanMessage] = [
    AIMessage(
        content="So you said you were researching LLM integrations?", name="Model"
    )
]
messages.append(HumanMessage(content="Yes, that's right.", name="Lance"))
messages.append(
    AIMessage(content="Great, what would you like to learn about", name="Model")
)
messages.append(
    HumanMessage(
        content="I want to learn about how to add unstructured documents (PDFs, DOCX, PPTX) to a RAG pipeline for langchain with ChatOllama and gemma4:26b with a local Chroma db."
        "I want to avoid any subscriptions or external servers if possible.",
        name="Lance",
    )
)
for message in messages:
    message.pretty_print()
# %%

llm = ChatOllama(model="gemma4:e4b", temperature=0.1)
result = llm.invoke(messages)  # note the return object type is already AIMessage
messages.append(result)
# %%
for message in messages:
    message.pretty_print()

# %%
# uncomment when running using script. For uv version use uv run streamlit run module-1/local_model/lesson3_chain.py
# note: streamlit formats the content very well. All the code will show up as code and tables will be rendered correctly
# st.title("List of messages")
# st.session_state.messages = messages
# for msg in messages:
#     if isinstance(msg, AIMessage):
#         st.chat_message("assistant").write(
#             msg.content
#         )  # remove .content to see the full JSON
#     else:
#         st.chat_message("human").write(msg.content)
# %%


# %%
# tool creation and call
def multiply(a: int | float, b: int | float) -> int | float:
    return a * b


def divide(a: int | float, b: int | float) -> int | float:
    if b != 0:
        return a / b
    else:
        raise ValueError("not divisable by b == 0")


def add(a: int | float, b: int | float) -> int | float:
    return a + b


def sub(a: int | float, b: int | float) -> int | float:
    return a - b


def pow(a: int | float, b: int | float) -> int | float:
    return a**b


def split_string(a: str) -> list:
    return [char for char in a]


def equals(a: str | float | int, b: str | float | int) -> bool:
    if type(a) is not type(b):
        return False
    return a == b


def convert_str_to_int(a: str) -> List[int]:
    return [ord(x) for x in a]


def greater_than(a: float | int, b: float | int) -> bool:
    if type(a) is not type(b):
        return False
    return a > b


def less_than(a: float | int, b: float | int) -> bool:
    if type(a) is not type(b):
        return False
    return a < b


_SCALAR_OPS = {
    "multiply": multiply,
    "divide": divide,
    "add": add,
    "sub": sub,
    "power": pow,
    "equals": equals,
    "greater_than": greater_than,
    "convert_str_to_int": convert_str_to_int,
    "less_than": less_than,
}


def apply_over_list(
    op_name: str, lst: List[int | float], operand: int | float
) -> List[int | float]:
    """
    Apply a two argument scalar scalar operation to every element of a list
    """
    if op_name not in _SCALAR_OPS:
        raise ValueError(f"unknown operation {op_name}; choose from {_SCALAR_OPS}")
    func = _SCALAR_OPS[op_name]
    return [func(x, operand) for x in lst]


def reduce_over_list(
    op_name: str,
    lst: List[int | float],
) -> int | float:
    """
    Apply a two argument scalar operation to a list and reduce the result
    """
    if op_name not in _SCALAR_OPS:
        raise ValueError(f"unknown operation {op_name} choose from {_SCALAR_OPS}")
    func = _SCALAR_OPS[op_name]
    return reduce(lambda acc, x: func(acc, x), lst)


# %%

llm = ChatOllama(model="gemma4:e4b", temperature=0.1)
llm_with_tools = llm.bind_tools(
    [
        multiply,
        divide,
        add,
        sub,
        pow,
        split_string,
        apply_over_list,
        reduce_over_list,
        equals,
        convert_str_to_int,
        greater_than,
        less_than,
    ]
)

# %%


# %%
tool_call = llm_with_tools.invoke(
    [
        HumanMessage(
            "What is the number of 'r's in strawberry. Use the provided tools to answer. The goal is to check if you can use multiple tools correctly. There are two tools you need to call.",
            name="Sohaib",
        )
    ]
)
pprint(
    tool_call.tool_calls
)  # THIS is a multi-tool call not one call so this does not work

# %%
pprint(tool_call.content)
# %%
_TOOLS = {
    "apply_over_list": apply_over_list,
    "reduce_over_list": reduce_over_list,
    "multiply": multiply,
    "divide": divide,
    "add": add,
    "sub": sub,
    "pow": pow,
    "split_string": split_string,
}

msg = llm_with_tools.invoke(
    [
        HumanMessage(
            "Take the list [1,2,3,4], add 10 to every element, then sum the results. "
            "Use the tools. You will need two tool calls."
        )
    ]
)

for call in msg.tool_calls:
    result = _TOOLS[call["name"]](**call["args"])
    print(call["name"], call["args"], "->", result)


def run_tool_messages(tool_messages):
    for _ in range(6):  # safety cap
        ai_msg = llm_with_tools.invoke(tool_messages)
        tool_messages.append(ai_msg)
        if not ai_msg.tool_calls:
            break
        for call in ai_msg.tool_calls:
            out = _TOOLS[call["name"]](**call["args"])
            tool_messages.append(ToolMessage(content=str(out), tool_call_id=call["id"]))
    for msg in tool_messages:
        msg.pretty_print()
    return tool_messages


# %%
initial_tool_check: List[AnyMessage] = [
    HumanMessage(
        "Take the list [1,2,3,4], add 10 to every element, then sum the results. "
        "Use the provided tools."
    )
]
initial_tool_check_result = run_tool_messages(initial_tool_check)


# %%
check_string_convert: List[AnyMessage] = [
    HumanMessage(
        "How many 'r' s are there in the word 'strawberrry'. Don't change the spelling and use the provided tools. "
    )
]

check_string_convert_result = run_tool_messages(check_string_convert)

# %%
check_equality_operators: List[AnyMessage] = [
    HumanMessage(
        "While the total is less than 10,000 multiple the values in the list [102, 100, 90, 101,100,110,110] by 10 and keep adding. What does the total come out to."
    )
]
check_equality_operators_result = run_tool_messages(check_equality_operators)
