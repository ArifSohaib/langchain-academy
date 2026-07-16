"""
script to run the interrupt using the server along with interrupts
note first start the correct server by using cd into `module-3-local` and running `uv run langgraph dev`
"""

# %%
from langchain_core.messages import  HumanMessage
from langgraph_sdk import get_client
from pprint import pprint
# %%
client = get_client(url="http://127.0.0.1:2024")
client_input = {"messages":[HumanMessage(content="multiply 34 by 56")]}

# %%


client_thread = await client.threads.create()
print(f"{client_thread=} {type(client_thread)=}")
# %%
async for chunk in client.runs.stream(
    thread_id=client_thread['thread_id'],
    assistant_id="agent",
    input= client_input,
    stream_mode="values",
    interrupt_before=["tools"]):
        print(f"Receiving new event of type :{chunk.event}")
        messages = chunk.data.get("messages",[])
        if messages:
            print(messages[-1])
        print("-"* 50)
# %%
async for chunk in client.runs.stream(
    thread_id=client_thread['thread_id'],
    assistant_id="agent",
    input=None,
    stream_mode="values",
    interrupt_before=["tools"]):
        print(f"receiving new event of type {chunk.event}...")
        messages = chunk.data.get("messages",[])
        if messages:
            if chunk.event == "values" and "content" in messages[-1]:
                pprint(messages[-1]['content'])
            else:
                print(messages[-1])

        print("*" * 50)
#%%
