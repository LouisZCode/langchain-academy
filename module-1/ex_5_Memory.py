from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver

#Lets send all the run information to langsmith
import os
os.environ["LANGCHAIN_PROJECT"] = "Academy_AgenthMemory"

load_dotenv()

#Memory Class
memory = MemorySaver()


# Tool
def multiply(a: int, b: int) -> int:
    """Multiplies a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b

def add(a: int, b: int) -> int:
    """Adds a and b.

    Args:
        a: first int
        b: second int
    """
    return a + b


def divide(a: int, b: int) -> int:
    """Divides a and b.

    Args:
        a: first int
        b: second int
    """
    return a / b


tools = [multiply, add, divide]

# LLM with bound tool
llm = ChatAnthropic(
    model="claude-3-sonnet-20240229",
    temperature=0
)

llm_with_tools = llm.bind_tools(tools)



# System message
sys_msg = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")


# Node
def assistant(state: MessagesState):
   return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}


# Build graph
builder = StateGraph(MessagesState)

builder.add_node("assistant_LLM", assistant)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "assistant_LLM")

builder.add_conditional_edges(
    "assistant_LLM",
    tools_condition,
)


builder.add_edge("tools", "assistant_LLM")

# Compile graph
react_graph_memory = builder.compile(checkpointer=memory)


#And lets add the Thread and give it an ID
config = {"configurable": {"thread_id": "1"}}


X =  input("You\n")
messages = [HumanMessage(content=f"{X}")]
messages = react_graph_memory.invoke({"messages" : messages}, config)  #   <---- Notice the new config variable here
for m in messages['messages']:
    m.pretty_print()