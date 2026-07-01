## Experiments
In module 1 starting with Chapter 3 I started testing out the tool use capabilities of gemma4:e4b to compare against the larger gemma4:26b. Both are running on AMD 7900 GRE with 16 GB RAM so the 26b model is hitting the limits therefore it is used less often but the idea is to check that when explicitly given tools in the file [tool_functions.py](module-1/local_model/tool_functions.py) and told to answer questions not from its own memory but only by referencing the tools does it correctly do it.


### Findings using simple graph with chains and tools

I started by giving it only the basic scaler arethmatic functions, a tool to apply functions to a list and a tool to apply a reduction to a list

1. The first experiment was to check if it could use multiple tools but ones I knew it had access to. I asked it to add 10 to every value of a random list and then sum the result of the list. 
"""
"Take the list [1,2,3,4], add 10 to every element, then sum the results. Use the provided tools."
"""
It correctly used the apply tool and then the reduce tool
```bash
================================ Human Message =================================
Take the list [1,2,3,4], add 10 to every element, then sum the results. Use the provided tools.
================================== Ai Message ==================================
Tool Calls:
  apply_over_list (68c64a07-ae1a-4bda-9d9f-2088d81b3e63)
 Call ID: 68c64a07-ae1a-4bda-9d9f-2088d81b3e63
  Args:
    lst: [1, 2, 3, 4]
    op_name: add
    operand: 10
================================= Tool Message =================================
[11, 12, 13, 14]
================================== Ai Message ==================================
Tool Calls:
  reduce_over_list (c6f3538f-fe7c-487c-a0da-1f6390232192)
 Call ID: c6f3538f-fe7c-487c-a0da-1f6390232192
  Args:
    lst: [11, 12, 13, 14]
    op_name: add
================================= Tool Message =================================
50
================================== Ai Message ==================================
The sum of the elements in the list [1, 2, 3, 4] after adding 10 to each element is 50.

```

2. For more complex scenario I asked it the famous "strawberry" qustion (count number of r s in strawberry) but deliberately misspelled to add an extra r 
For this one, in addition to the previous tools I gave it additional functions to split the string and convert characters to integers
The specific question was:
"""
"How many 'r' s are there in the word 'strawberrry'. Don't change the spelling and use the provided tools. "
"""
It correctly used the split string tool but counted the number of 'r' values directly from the result without using any tool
```bash
================================ Human Message =================================
How many 'r' s are there in the word 'strawberrry'. Don't change the spelling and use the provided tools.
================================== Ai Message ==================================
Tool Calls:
  split_string (964b939a-175e-4b9c-96a1-5da7960048d2)
 Call ID: 964b939a-175e-4b9c-96a1-5da7960048d2
  Args:
    a: strawberrry
================================= Tool Message =================================
['s', 't', 'r', 'a', 'w', 'b', 'e', 'r', 'r', 'r', 'y']
================================== Ai Message ==================================
There are 4 'r's in the word 'strawberrry'.

```


3. I tested a function that would mostly work with the given tools but an additional caviet that might require it to use a while loop which in the original tool_functions I did not give it access to. 
However it did have access to three equality tools (equals, less_than, greater than)

The specific question was:
"""
"While the total is less than 10,000 multiple the values in the list [102, 100, 200, 150, 101, 90, 101,100,110,110,] by 10 and keep adding. What does the total come out to BEFORE reaching 10,000. Use the provided tools, I am trying to test if you can call tools correctly and link their inputs/outputs as needed.
"""
Note that in this case I explicitly told it that it is being tested. To test this one I changed the apply function and the reduce function to allow it to use a condition defined as a bool input. 
After debugging I found out that the tool can not use conditions directly and conditional application is much more involved. The initial step is to start the condition as a string.



### Findings using tools
Results are shown in [lesson4_routers.py](module-1/local_model/lesson4_routers.py)
Testing with routers, first problem I found is that the tools do not work unless they are given explicit doc strings.

Tool router needs to be routed back to the llm after a tool call.
Tool use with router seems to be better because for the more coomplex query: (query 3) it adds values individually and stops right before the condition is reached. In the previous version it ran the apply on list tool and picked the value that satisfied the condition.


I added edges increuemtally. First graph was:
```python
builder = StateGraph(MessagesState)
builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_node("tools", ToolNode([multiply, add, divide, pow]))
builder.add_edge(START, "tool_calling_llm")
builder.add_conditional_edges("tool_calling_llm", tools_condition)
builder.add_edge("tools", END)
builder.add_edge("tool_calling_llm", END)
graph = builder.compile()
```

Then I added:
```python
builder.add_edge("tools", "tool_calling_llm")
```
This allows the tools to not just end but to go back to the calling llm with the result. 
This was when the tool was able to incrementally use the add operation.

NOTE: adding `builder.add_edge("tool_calling_llm", "tool_calling_llm")` to allow the output of an llm to go back to the llm without a tool call results in an infinite loop.
This is what the agent and the "re-act" (act, observe, reason) pattern fixes.


After adding a simple agent with doc strings for each tool and allowing the equals tool to use string, int or float as inputs, it was not able to apply the function correctly.
Then because it was not able to use the equals tool correctly, it resulted in the answer 3 instead of 4.

```bash
================================ Human Message =================================
How many 'r' s are there in the word 'strawberrry'. Don't change the spelling and use the provided tools.
================================== Ai Message ==================================
Tool Calls:
  split_string (7ef15a6b-482a-472a-bff4-f05b250ee325)
 Call ID: 7ef15a6b-482a-472a-bff4-f05b250ee325
  Args:
    a: strawberrry
================================= Tool Message =================================
Name: split_string
["s", "t", "r", "a", "w", "b", "e", "r", "r", "r", "y"]
================================== Ai Message ==================================
Tool Calls:
  apply_over_list (80c320bc-26a1-4cfd-b6b2-87e355027d1f)
 Call ID: 80c320bc-26a1-4cfd-b6b2-87e355027d1f
  Args:
    lst: ['s', 't', 'r', 'a', 'w', 'b', 'e', 'r', 'r', 'r', 'y']
    op_name: equals
    operand: r
================================= Tool Message =================================
Name: apply_over_list
Error invoking tool 'apply_over_list' with kwargs {'lst': ['s', 't', 'r', 'a', 'w', 'b', 'e', 'r', 'r', 'r', 'y'], 'op_name': 'equals', 'operand': 'r'} with error:
 lst.0.int: Input should be a valid integer, unable to parse string as an integer
lst.0.float: Input should be a valid number, unable to parse string as a number
lst.1.int: Input should be a valid integer, unable to parse string as an integer
lst.1.float: Input should be a valid number, unable to parse string as a number
lst.2.int: Input should be a valid integer, unable to parse string as an integer
lst.2.float: Input should be a valid number, unable to parse string as a number
lst.3.int: Input should be a valid integer, unable to parse string as an integer
lst.3.float: Input should be a valid number, unable to parse string as a number
lst.4.int: Input should be a valid integer, unable to parse string as an integer
lst.4.float: Input should be a valid number, unable to parse string as a number
lst.5.int: Input should be a valid integer, unable to parse string as an integer
lst.5.float: Input should be a valid number, unable to parse string as a number
lst.6.int: Input should be a valid integer, unable to parse string as an integer
lst.6.float: Input should be a valid number, unable to parse string as a number
lst.7.int: Input should be a valid integer, unable to parse string as an integer
lst.7.float: Input should be a valid number, unable to parse string as a number
lst.8.int: Input should be a valid integer, unable to parse string as an integer
lst.8.float: Input should be a valid number, unable to parse string as a number
lst.9.int: Input should be a valid integer, unable to parse string as an integer
lst.9.float: Input should be a valid number, unable to parse string as a number
lst.10.int: Input should be a valid integer, unable to parse string as an integer
lst.10.float: Input should be a valid number, unable to parse string as a number
operand.int: Input should be a valid integer, unable to parse string as an integer
operand.float: Input should be a valid number, unable to parse string as a number
 Please fix the error and try again.
================================== Ai Message ==================================
There are 3 'r's in the word 'strawberrry'.

```
Removing the str option from equals, results in the agent using the split_string function and counting from the results instead of using any other tool.

```bash
================================ Human Message =================================
How many 'r' s are there in the word 'strawberrry'. Don't change the spelling and use the provided tools.
================================== Ai Message ==================================
Tool Calls:
  split_string (9ee4496b-1dc1-4e25-8181-36f1bfe65644)
 Call ID: 9ee4496b-1dc1-4e25-8181-36f1bfe65644
  Args:
    a: strawberrry
================================= Tool Message =================================
Name: split_string
["s", "t", "r", "a", "w", "b", "e", "r", "r", "r", "y"]
================================== Ai Message ==================================
There are 4 'r's in the word 'strawberrry'.

```


For the more complex question it used the tools correctly and adds values in the list individually instead of reading the output and trying to use the llm to generate the answer.
```bash
================================ Human Message =================================
While the total is less than 10,000 multiple the values in the list [102, 100, 200, 150, 101, 90, 101,100,110,110,] by 10 and keep adding. What does the total come out to BEFORE reaching 10,000. Use the provided tools.
================================== Ai Message ==================================
Tool Calls:
  apply_over_list (a5dd6e34-3f6a-4abe-aac1-3dd26892e465)
 Call ID: a5dd6e34-3f6a-4abe-aac1-3dd26892e465
  Args:
    lst: [102, 100, 200, 150, 101, 90, 101, 100, 110, 110]
    op_name: multiply
    operand: 10
================================= Tool Message =================================
Name: apply_over_list
[1020, 1000, 2000, 1500, 1010, 900, 1010, 1000, 1100, 1100]
================================== Ai Message ==================================
Tool Calls:
  add (c204b719-c480-4be9-b0f1-032a43c1798b)
 Call ID: c204b719-c480-4be9-b0f1-032a43c1798b
  Args:
    a: 1020
    b: 1000
================================= Tool Message =================================
Name: add
2020
================================== Ai Message ==================================
Tool Calls:
  add (c23676bb-1492-46f9-9297-5d5c1e27c6a9)
 Call ID: c23676bb-1492-46f9-9297-5d5c1e27c6a9
  Args:
    a: 2020
    b: 2000
================================= Tool Message =================================
Name: add
4020
================================== Ai Message ==================================
Tool Calls:
  add (22feccf4-f41f-40c8-baab-e52ff19a8a78)
 Call ID: 22feccf4-f41f-40c8-baab-e52ff19a8a78
  Args:
    a: 4020
    b: 1500
================================= Tool Message =================================
Name: add
5520
================================== Ai Message ==================================
Tool Calls:
  add (4b7a601c-cc49-48be-9f70-2bac039f843e)
 Call ID: 4b7a601c-cc49-48be-9f70-2bac039f843e
  Args:
    a: 5520
    b: 1010
================================= Tool Message =================================
Name: add
6530
================================== Ai Message ==================================
Tool Calls:
  add (e3e22baa-0b5d-496e-af8b-de7735c5e445)
 Call ID: e3e22baa-0b5d-496e-af8b-de7735c5e445
  Args:
    a: 6530
    b: 900
================================= Tool Message =================================
Name: add
7430
================================== Ai Message ==================================
Tool Calls:
  add (4d4feaf3-558a-482f-932e-2cf5df890028)
 Call ID: 4d4feaf3-558a-482f-932e-2cf5df890028
  Args:
    a: 7430
    b: 1010
================================= Tool Message =================================
Name: add
8440
================================== Ai Message ==================================
Tool Calls:
  add (1aacf027-68ed-4f7d-be97-a4b0dc0bd48f)
 Call ID: 1aacf027-68ed-4f7d-be97-a4b0dc0bd48f
  Args:
    a: 8440
    b: 1000
================================= Tool Message =================================
Name: add
9440
================================== Ai Message ==================================
The total comes out to **9440**.

```
