"""
Since the search part of parallel execution is very different since the original couse, I am moving it here.
Main change is that I am not using the langchain_community based modules since they are deprecated
"""
# %%
from IPython.display import display, Image, Markdown
from langchain.messages import AIMessage, SystemMessage, HumanMessage, AnyMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.errors import EmptyInputError
from langchain_ollama import ChatOllama
from typing import TypedDict, Annotated, Any
from langchain_tavily import TavilySearch
from langgraph.errors import InvalidUpdateError, NodeInterrupt
from langchain_core.documents import Document
from utils import get_wiki_content, extract_json
import operator
from typing import Annotated
from langgraph.types import Send
# %%

class SearchState(MessagesState):
    questions: list[str]
    question: str
    max_doc_count: int
    answer_docs: Annotated[list[Document], operator.add]
    found_docs: Annotated[int, operator.add]

# %%
def web_search(state: SearchState):
    """
    retrieve documents from tavily search
    """
    tavily_search = TavilySearch(max_results=state['max_doc_count'])
    data = tavily_search.invoke({"query": state["question"]})
    search_docs = data.get("results", data)
    documents: list[Document] = []
    for doc in search_docs:
        document = Document(page_content=doc['content'], title=doc['title'], metadata={"source": doc['url'], "score": doc['score']})
        documents.append(document)
    # note: no "question" key here — avoids concurrent-write conflicts across parallel branches
    return {"found_docs": len(documents), "answer_docs": documents}

# %%
def wikipedia_search(state: SearchState):
    """
    retrieve list of documents from Wikipedia api
    """
    answer_docs = get_wiki_content(state['question'],state['max_doc_count'])
    return {"found_docs":len(answer_docs), "answer_docs":answer_docs}
# %%
llm = ChatOllama(model="gemma4:e4b")

# %%


def get_questions(state: SearchState):
    sys_message = SystemMessage(content="""
        you are a helpful search agent you will take the user's query and generate a list of terms to use for search in wikipedia.
        Remember that wikipedia does not support direct questions so word the terms in manner of topics it would have.
        Respond ONLY in the json format with the word "questions" as the key and a list of string values as the value.
        DO NOT use any other key and DO NOT RETURN anything other than the JSON
        """)
    question = [sys_message] + [state['messages'][-1]]
    result = llm.invoke(question)
    try:
        json_result = extract_json(str(result.content))
    except Exception as ex:
        return {"messages": [result] + [AIMessage(content=f"error: {ex}")], "questions": []}
    return {"questions": json_result.get("questions", []), "messages": [result]}

def continue_to_web_search(state: SearchState):
    """
    fan out: spawn one web_search branch per generated question
    """
    max_doc_count = state.get("max_doc_count", 5)
    return [
        Send("web_search", {"question": q, "max_doc_count": max_doc_count})
        for q in state["questions"]
    ]


def continue_to_wiki_search(state: SearchState):
    """
    fan out: spawn one web_search branch per generated question
    """
    max_doc_count = state.get("max_doc_count", 5)
    return [
        Send("wikipedia_search", {"question": q, "max_doc_count": max_doc_count})
        for q in state["questions"]
    ]

search_builder = StateGraph(SearchState)
search_builder.add_node("get_questions", get_questions)
search_builder.add_node("web_search", web_search)
search_builder.add_node("wikipedia_search", wikipedia_search)
search_builder.add_edge(START, "get_questions")
# search_builder.add_conditional_edges("get_questions", continue_to_web_search, ["web_search"])
search_builder.add_conditional_edges("get_questions", continue_to_wiki_search, ["wikipedia_search"])
# search_builder.add_edge("web_search", END)
search_builder.add_edge("wikipedia_search", END)
search_graph = search_builder.compile(checkpointer=MemorySaver())
# %%
display(Image(search_graph.get_graph().draw_mermaid_png()))
# %%
test_search = HumanMessage(content="graph algorithms")
search_graph_result = search_graph.invoke({"messages":[test_search]}, {"configurable":{"thread_id":"1"}})
# %%
print(search_graph_result.keys())

# %%
print(extract_json(search_graph_result['messages'][-1].content))
# %%
print(search_graph_result['answer_docs'][0].metadata)
# %%
for doc in search_graph_result['answer_docs']:
    print(doc.metadata['source'])
# %%
display(Markdown(search_graph_result['answer_docs'][0].page_content))
# %%
graph_hist = [h for h in search_graph.get_state_history({"configurable":{"thread_id":"1"}})]

# %%

print(graph_hist[-1].values)

# %%
print(graph_hist[-3].values['questions'])
# %%
