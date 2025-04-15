from langgraph_sdk import get_client
from langchain_core.messages import HumanMessage

# Input
input = {"messages": [HumanMessage(content="Multiply 3 by 2.")]}

async def main():
    # This is the URL of the local development server
    URL = "http://127.0.0.1:2024"
    client = get_client(url=URL)

    # Search all hosted graphs
    assistants = await client.assistants.search()
    print(assistants [1])

    # We create a thread for tracking the state of our run
    thread = await client.threads.create()

    async for chunk in client.runs.stream(
        thread['thread_id'],
        "agent",
        input=input,
        stream_mode="values",
    ):
        if chunk.data:
            if chunk.event == "metadata":
                print("\nMetadata:", chunk.data)
            else:
                print(chunk.data['messages'][-1])

# Run the async function
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
