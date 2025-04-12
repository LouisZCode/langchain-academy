from pprint import pprint
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_anthropic import ChatAnthropic
from typing import TypedDict
#This seems to be  a placeholder for... you guessed it... any message
from langchain_core.messages import AnyMessage
#Lets also get the important modules so we can use Reducer and not only overwrite our messages:
from typing import Annotated
from langgraph.graph.message import add_messages
#Lets get what we need to create the Graph
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END


# Load environment variables from .env file
load_dotenv()


# Using Claude
llm = ChatAnthropic(
    model="claude-3-sonnet-20240229",
    temperature=0
)

human_says = input("You:\n")


#NOTE STATE
#Here we create the state
class MessageState(TypedDict):
    #...and also we add a reducer so to not overwrite all our messages.
    messages: Annotated[list[AnyMessage], add_messages]


#NOTE NODE
def tool_calling_llm(state: MessageState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}



#NOTE TOOL
# Define a  tool
def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b


# Bind the tool to the LLM
llm_with_tools = llm.bind_tools([multiply])

#NOTE Build the Graph:
builder = StateGraph(MessageState)
builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_edge(START, "tool_calling_llm")
builder.add_edge("tool_calling_llm", END)
graph = builder.compile()

# View
#display(Image(graph.get_graph().draw_mermaid_png()))

#Here we have the original message
messages = graph.invoke({"messages": HumanMessage(content=f"{human_says}", name="Luis")})
for m in messages['messages']:
    m.pretty_print()



