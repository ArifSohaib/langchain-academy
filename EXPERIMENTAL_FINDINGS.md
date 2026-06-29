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
