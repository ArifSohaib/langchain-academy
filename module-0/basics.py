# %%

from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama

## Use Shift + Ctrl + Enter to run as a cell
# %%
gemma4_e4b_chat = ChatOllama(model="gemma4:e4b")
gemma4_26b_chat = ChatOllama(model="gemma4:26b")

# %%


msg = HumanMessage(content="Hello world", name="Sohaib")

messages = [msg]
e4b_invoke_result = gemma4_e4b_chat.invoke(messages)
# %%
print(e4b_invoke_result)
# %%
