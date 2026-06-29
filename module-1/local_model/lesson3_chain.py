# %%

from pprint import pprint
from typing import List

from IPython.display import Image, Markdown, display

# import streamlit as st
# from langchain_core.callbacks.manager import Func
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.graph.message import AnyMessage, add_messages
from tool_functions import _TOOLS, tool_list
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

""" Uncomment when running using script. For uv version use uv run streamlit run module-1/local_model/lesson3_chain.py
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

"""


""" Uncomment to see tool use on one turn conversation. This will only call the tool but not use its results in the resulting message
llm = ChatOllama(model="gemma4:e4b", temperature=0.1)
tool_list = [
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
    remove_from_end_of_list,
    remove_from_list,
]
llm_with_tools = llm.bind_tools(tool_list)

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

pprint(tool_call.content)
"""


# %%
def run_tool_messages(
    tool_messages, model: str, tool_list: List[Callable], safety_cap: int = 6
):
    llm = ChatOllama(model=model, temperature=0.1)
    llm_with_tools = llm.bind_tools(tool_list)
    for _ in range(safety_cap):  # safety cap
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
initial_tool_check_result = run_tool_messages(
    initial_tool_check, "gemma4:e4b", tool_list
)
# %%
code_question = """How can I corret the following function to be used as a tool in llms such that it is able to reduce over a list OPTIONALLY based on a provided condition.
The corrected version should run for both while conditions and if conditions.
def reduce_over_list(
    op_name: str, lst: List[int | float], cond: Optional[bool]
) -> int | float:
    '''
    Apply a two argument scalar operation to a list and reduce the result
    '''
    if op_name not in _SCALAR_OPS:
        raise ValueError(f"unknown operation {op_name} choose from {_SCALAR_OPS}")
    if len(lst) == 0:
        raise ValueError("empty list can't be reduced")
    func = _SCALAR_OPS[op_name]
    if cond is not None:
        cond_list = [x for x in lst if cond]
        return reduce(lambda acc, x: func(acc, x), cond_list)
    return reduce(lambda acc, x: func(acc, x), lst)


"""
# %%

# %%
code_question_llm = ChatOllama(model="gemma4:26b")
code_question_llm_messages = [HumanMessage(content=code_question)]
code_question_result = code_question_llm.invoke(code_question_llm_messages)
# %%

display(Markdown(code_question_result.content))
# %%
check_string_convert: List[AnyMessage] = [
    HumanMessage(
        "How many 'r' s are there in the word 'strawberrry'. Don't change the spelling and use the provided tools. "
    )
]

check_string_convert_result = run_tool_messages(
    check_string_convert, "gemma4:e4b", tool_list
)

# %%
check_equality_operators: List[AnyMessage] = [
    HumanMessage(
        "While the total is less than 10,000 multiple the values in the list [102, 100, 200, 150, 101, 90, 101,100,110,110,] by 10 and keep adding. What does the total come out to BEFORE reaching 10,000. Use the provided tools, I am trying to test if you can call tools correctly and link their inputs/outputs as needed."
    )
]
check_equality_operators_result = run_tool_messages(
    check_equality_operators, "gemma4:e4b", tool_list
)
# %%
for msg in check_equality_operators_result:
    pprint(msg.pretty_print())
    if isinstance(msg, AIMessage):
        print(msg.tool_calls)


# %%
# Message State and Annotations
initial_messages = [
    AIMessage(content="Hello! How can I assist you?", name="Model"),
    HumanMessage(
        content="I'm looking for information on running local LLMs using LangGraph with custom documents in PDF, DOCX, XLSX and PPTX",
        name="Sohaib",
    ),
]

new_message = AIMessage(
    content="Sure, I can help with that. What specifically are you interested in?",
    name="Model",
)

add_messages(initial_messages, new_message)


# %%
llm = ChatOllama(model="gemma4:e4b", temperature=0.1)
llm_with_tools = llm.bind_tools(tool_list)


def tool_calling_llm(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


# %%
builder = StateGraph(MessagesState)
builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_edge(START, "tool_calling_llm")
builder.add_edge("tool_calling_llm", END)
graph = builder.compile()
# %%

display(Image(graph.get_graph().draw_mermaid_png()))
# %%
