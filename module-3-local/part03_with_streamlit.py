"""Streamlit UI for the human-in-the-loop arithmetic agent.

Run with:
    streamlit run app.py

Everything runs locally: open-source langgraph + Ollama. No API keys needed.
Deps: pip install streamlit langgraph langgraph-checkpoint-sqlite langchain-ollama
"""

import sqlite3
from pathlib import Path
from uuid import uuid4

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from simple_tools import add, sub, multiply, divide, apply_to_list, split_string, convert_string_to_ord

st.set_page_config(page_title="Arithmetic agent", page_icon="🧮")


# ---------------------------------------------------------------------------
# Build the graph ONCE per server process.
# Streamlit reruns this file top-to-bottom on every interaction, so without
# cache_resource you would recompile the graph and reopen sqlite every click.
# ---------------------------------------------------------------------------
@st.cache_resource
def build_graph():
    tools = [add, sub, multiply, divide, apply_to_list, split_string, convert_string_to_ord]
    llm = ChatOllama(model="gemma4:e4b", temperature=0.1)
    llm_with_tools = llm.bind_tools(tools)

    sys_msg = SystemMessage(
        content="You are a helpful assistant tasked with performing arithmetic on a set of inputs."
    )

    def assistant(state: MessagesState):
        return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

    builder = StateGraph(MessagesState)
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")

    Path("state_db").mkdir(exist_ok=True)
    # check_same_thread=False matters: Streamlit calls into this from
    # different threads across reruns.
    conn = sqlite3.connect("state_db/streamlit_agent.db", check_same_thread=False)
    return builder.compile(interrupt_before=["assistant"], checkpointer=SqliteSaver(conn))


graph = build_graph()

# ---------------------------------------------------------------------------
# Thread management: one thread_id per browser session, resettable.
# All chat history lives in the checkpointer under this id, so we never
# store messages in session_state ourselves.
# ---------------------------------------------------------------------------
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid4())

with st.sidebar:
    st.subheader("Conversation thread")
    st.code(st.session_state.thread_id, language=None)
    if st.button("New conversation"):
        st.session_state.thread_id = str(uuid4())
        st.rerun()
    auto_continue = st.toggle(
        "Auto-continue after my edit",
        value=True,
        help=(
            "interrupt_before=['assistant'] pauses EVERY time the assistant is "
            "about to run, including after each tool call. When on, only the "
            "first pause (where you can edit) requires a click; the rest run "
            "through automatically."
        ),
    )

thread = {"configurable": {"thread_id": st.session_state.thread_id}}


def run_segment(graph_input):
    """Stream one segment: until END or the next interrupt.

    We don't need the streamed events for display — every step is
    checkpointed, and the UI re-renders from graph.get_state() below.
    """
    with st.spinner("Thinking..."):
        for _ in graph.stream(graph_input, config=thread, stream_mode="values"):
            pass


def resume(auto: bool):
    """Resume from an interrupt; optionally keep going through later pauses."""
    run_segment(None)
    if auto:
        while graph.get_state(thread).next:
            run_segment(None)


def render(messages):
    for msg in messages:
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.markdown(msg.content)
        elif isinstance(msg, AIMessage):
            with st.chat_message("assistant"):
                if msg.content:
                    st.markdown(msg.content)
                for tc in msg.tool_calls:
                    st.caption(f"🔧 calling `{tc['name']}` with `{tc['args']}`")
        elif isinstance(msg, ToolMessage):
            with st.chat_message("assistant"):
                st.caption(f"↩️ `{msg.name}` returned `{msg.content}`")


# ---------------------------------------------------------------------------
# Render current state, then decide which controls to show.
# ---------------------------------------------------------------------------
st.title("Local LangGraph agent")

state = graph.get_state(thread)
render(state.values.get("messages", []))

paused_before = state.next  # e.g. ('assistant',) while interrupted, () when idle

if paused_before:
    st.info(f"⏸️ Paused before node(s): **{', '.join(paused_before)}**")

    # Key the text box to the current checkpoint so it clears itself after
    # each resume instead of resubmitting the old correction.
    ckpt = state.config["configurable"].get("checkpoint_id", "start")
    correction = st.text_input(
        "Optional correction or extra instruction (appended before the model runs)",
        key=f"edit-{ckpt}",
        placeholder="e.g. no, actually use the list [1,3,5,7,9,11]",
    )

    col_edit, col_continue = st.columns(2)
    if col_edit.button("Apply edit & continue", disabled=not correction.strip(), width="stretch"):
        # Same as the notebook: append a HumanMessage via update_state, then
        # resume with the *thread* config (never a config with checkpoint_id).
        graph.update_state(thread, {"messages": [HumanMessage(content=correction.strip())]})
        resume(auto_continue)
        st.rerun()

    if col_continue.button("Continue as-is", width="stretch"):
        resume(auto_continue)
        st.rerun()
else:
    prompt = st.chat_input("Ask for some arithmetic...")
    if prompt:
        # New user turn: run until the first interrupt (before assistant).
        run_segment({"messages": [HumanMessage(content=prompt)]})
        st.rerun()
