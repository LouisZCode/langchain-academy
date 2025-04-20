from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition

from langgraph.graph import MessagesState
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.messages import HumanMessage


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
    tools_condition,
)
builder.add_edge("tools", END)

memory = MemorySaver()
graph = builder.compile(interrupt_before=["tools"], checkpointer=memory)

# Input
initial_input = {"messages": HumanMessage(content="Multiply 2 and 3")}

# Thread
thread = {"configurable": {"thread_id": "1"}}

# Run the graph until the first interruption
for event in graph.stream(initial_input, thread, stream_mode="values"):
    event['messages'][-1].pretty_print()

#print which is the next node:
state = graph.get_state(thread)
print(f"\nThe next checkpoint is:\n{state.next}")


# Get user feedback
user_approval = input("\nDo you want to call the tool? (yes/no):\n")

if user_approval.lower() == "yes":
#If we call.stream pass a NONE and give it the Thread ID…
# it will re-execute form the current checkpoint, like this:
#We can start the graph from any point in time...!
    for event in graph.stream(None, thread, stream_mode="values"):
        event['messages'][-1].pretty_print()
else:
    print("Operation cancelled by user.")