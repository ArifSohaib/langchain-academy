# %%
import wikipediaapi
from dotenv import load_dotenv
from langchain_core.documents import Document
import json
# %%
load_dotenv()

# %%
def extract_json(text: str) -> dict:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError(f"No JSON object found in response: {text!r}")
    return json.loads(text[start:end + 1])

# %%
wiki = wikipediaapi.Wikipedia(
    user_agent="langchain-academy-tutorial/0.1 (you@example.com)",
    language="en",
)

# %%
def get_wiki_content(query: str, num_docs: int = 10) -> list[Document]:
    """
    utility function to get wikipedia docs
    """
    results = wiki.search(query, limit=num_docs)  # search() already returns real pages
    docs = []
    for title, page in results.pages.items():
        if not page.exists():
            continue
        docs.append(
            Document(
                page_content=page.summary,
                metadata={"source": page.fullurl, "title": page.title},
            )
        )
        if len(docs) >= num_docs:
            break
    return docs
