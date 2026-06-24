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


_SCALAR_OPS = {
    "multiply": multiply,
    "divide": divide,
    "add": add,
    "sub": sub,
    "power": pow,
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
    op_name: str, lst: List[int | float], operand: int | float
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
    [multiply, divide, add, sub, pow, split_string, apply_over_list, reduce_over_list]
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
# %%
messages_tool_check: List[AnyMessage] = [
    HumanMessage(
        "Take the list [1,2,3,4], add 10 to every element, then sum the results. "
        "Use the provided tools."
    )
]

# %%
for _ in range(6):  # safety cap
    ai_msg = llm_with_tools.invoke(messages_tool_check)
    messages_tool_check.append(ai_msg)
    if not ai_msg.tool_calls:
        break
    for call in ai_msg.tool_calls:
        out = _TOOLS[call["name"]](**call["args"])
        messages_tool_check.append(
            ToolMessage(content=str(out), tool_call_id=call["id"])
        )
# %%
pprint(messages_tool_check[-1].content)
# ##
pprint(messages_tool_check)
# %%
