from typing import TypedDict, Literal
import random
#Loos like this is a Module that helps create quick graphs with Python..!
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END

#NOTE STATE

#This makes all the dinctionaries created from a class require a str to tell the "graph_state"
class State(TypedDict):
    #This would be the Keys, we need only one for this simple exercise
    graph_state: str


#NOTE NODES

#These update the state.
#Now lets define our Nodes. Nodes are simple Python functions, where the first argument is the state.
def node_1(state):
    print("---Node 1---")
    #we can extract the value of "graph state" the key, and each node will overwrite the value of graph state
    #with something new
    #In this Node 1, we take the value of graps tsate ("") and we append "I am"
    return {"graph_state": state['graph_state'] +" I am"}

def node_2(state):
    print("---Node 2---")
    return print({"graph_state": state['graph_state'] +" happy!"})

def node_3(state):
    print("---Node 3---")
    return print({"graph_state": state['graph_state'] +" sad!"})


#NOTE EDGES

def decide_mood(state) -> Literal["node_2", "node_3"]:
    
    #Often, we will use the state to decide on the next node to visit
    user_input = state["graph_state"]

    #Lets do a random 50% chance
    if random.random() < 0.5:
        return "node_2"
    return "node_3"


#NOTE GRAPH

#Build a Graph
#First, we initialize our StateGraph with the State class we created above
builder = StateGraph(State)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)
#Note that this is dependant of what NODES were created before, so a Node 4 is not possible
#Not possible:  builder.add_node("node_4", node_4)

#Logic
#We use a special Class called START which is the starting node in the Graph
builder.add_edge(START, "node_1")
#now for a conditiona edge, from node 1 to the function that divides the directions
builder.add_conditional_edges("node_1", decide_mood)
#and now 2 last edges, with the END class, meaning, final node
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

# We compile the graph now that we are done!
graph = builder.compile()

#And we can even see the graph:   Just take away the #
display(Image(graph.get_graph().draw_mermaid_png()))

#NOTE INVOCATION
#When invoke is called, the graph starts execution from the START node and then it goes in order until the
#END node is reached.
#Each Node receives the current state and overrides it...
graph.invoke({"graph_state" : "Hi  whatever initial string here,"})
