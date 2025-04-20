from pprint import pprint
from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage, trim_messages, SystemMessage
from dotenv import load_dotenv
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import MemorySaver
import asyncio

load_dotenv()

# Using Claude
llm = ChatAnthropic(
    model="claude-3-sonnet-20240229",
    temperature=0
)


class State(MessagesState):
    summary: str


# Define the logic to call the model
def call_model(state: State):
    
    # Get summary if it exists
    summary = state.get("summary", "")

    # If there is summary, then we add it
    if summary:
        
        # Add summary to system message
        system_message = f"Summary of conversation earlier: {summary}"

        # Append summary to any newer messages
        messages = [SystemMessage(content=system_message)] + state["messages"]
    
    else:
        messages = state["messages"]
    
    response = llm.invoke(messages)
    return {"messages": response}


def summarize_conversation(state: State):
    
    # First, we get any existing summary
    summary = state.get("summary", "")

    # Create our summarization prompt 
    if summary:
        
        # A summary already exists
        summary_message = (
            f"This is summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )
        
    else:
        summary_message = "Create a summary of the conversation above:"

    # Add prompt to our history
    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = llm.invoke(messages)
    
    # Delete all but the 2 most recent messages
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": response.content, "messages": delete_messages}


def should_continue(state: State):
    
    """Return the next node to execute."""
    
    messages = state["messages"]
    
    # If there are more than six messages, then we summarize the conversation
    if len(messages) > 6:
        return "summarize_conversation"
    
    # Otherwise we can just end
    return END


# Define a new graph
workflow = StateGraph(State)
workflow.add_node("conversation", call_model)
workflow.add_node(summarize_conversation)

# Set the entrypoint as conversation
workflow.add_edge(START, "conversation")
workflow.add_conditional_edges("conversation", should_continue)
workflow.add_edge("summarize_conversation", END)


# Compile
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)


async def main():
    node_to_stream = 'conversation'
    config = {"configurable": {"thread_id": "4"}}
    input_message = HumanMessage(content="Tell me about the 49ers NFL team")
    async for event in graph.astream_events({"messages": [input_message]}, config, version="v2"):
    # Get chat model tokens from a particular node 
        if event["event"] == "on_chat_model_stream" and event['metadata'].get('langgraph_node','') == node_to_stream:
            print(event["data"])

if __name__ == "__main__":
    asyncio.run(main())
