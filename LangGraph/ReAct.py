from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode


load_dotenv()


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


@tool
def add(a: int, b:int):
    """This function adds two numbers"""

    return a + b

@tool
def subtract(a: int, b: int):
    """This function subtracts two numbers"""

    return a - b

tools = [add, subtract]

llm_name = "llama-3.3-70b-versatile"
llm = ChatGroq(model=llm_name).bind_tools(tools)


def llm_call(state: AgentState) -> AgentState:

    system_prompt = SystemMessage(content="You are my AI assistant, Please answer my query to the best of your ability")

    response = llm.invoke([system_prompt] + state["messages"])

    return {"messages": [response]}

def should_continue(state: AgentState):

    messages = state["messages"]
    last_message = messages[-1]

    if last_message.tool_calls:

        return "continue"
    else:

        return "end"
    


## Create graph

graph = StateGraph(AgentState)
tool_node = ToolNode(tools=tools)

graph.add_node("llm_call", llm_call)
graph.add_node("tool_node", tool_node)


graph.add_edge(START, "llm_call")
graph.add_conditional_edges(
    "llm_call",
    should_continue,

    {
        "continue": "tool_node",
        "end": END
    }
)

graph.add_edge("tool_node", "llm_call")


app = graph.compile()



def print_stream(stream):

    for s in stream:

        message = s['messages'][-1]

        if isinstance(message, tuple):

            print(message)
        else:

            message.pretty_print()


user_input = input("\nEnter prompt: ")

while user_input != "exit":


    stream = app.stream(AgentState(messages=[user_input]), stream_mode="values")

    print("\n")

    print_stream(stream)

    user_input = input("\n\nEnter prompt: ")