from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

#Useless vies of the graph here:
from IPython.display import Image, display

#Here are prebuilt elements from LangGraph, more to be found here: https://langchain-ai.github.io/langgraph/reference/prebuilt/
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition

#Lets import the mesageState class from LG
from langgraph.graph import MessagesState
from langgraph.graph import START, END, StateGraph

#For emssages into the State:
from langchain_core.messages import HumanMessage


# Load environment variables from .env file
load_dotenv()


#TOOL
def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b


# Using Claude
llm = ChatAnthropic(
    model="claude-3-sonnet-20240229",
    temperature=0
)

llm_with_tools = llm.bind_tools([multiply])

#Node
def tool_calling_llm(state: MessagesState):
    return {"messages" : [llm_with_tools.invoke(state["messages"])]}

#Build The Graph!
builder = StateGraph(MessagesState)
builder.add_edge(START, "tool_calling_llm")
builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_node("tools", ToolNode([multiply]))
builder.add_conditional_edges(
    "tool_calling_llm",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", END)
graph = builder.compile()

# View
#display(Image(graph.get_graph().draw_mermaid_png()))

X =  input("You\n")
messages = [HumanMessage(content=f"{X}")]
messages = graph.invoke({"messages" : messages})
for m in messages['messages']:
    m.pretty_print()