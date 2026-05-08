import os

from typing import TypedDict, List, Union
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_groq import ChatGroq
from IPython.display import display, Image
from dotenv import load_dotenv


load_dotenv()

llm_name = "llama-3.3-70b-versatile"
llm = ChatGroq(model=llm_name)


class AgentState(TypedDict):
    messages: List[Union[HumanMessage, AIMessage]]




def process(state: AgentState) -> AgentState:
    """This node will solve the request you input"""

    ai_response = llm.invoke(state['messages'])
    state['messages'].append(AIMessage(content=ai_response.content))

    print(f"\nAI: {ai_response.content}")

    return state


graph = StateGraph(AgentState)

graph.add_node("process", process)
graph.add_edge(START, "process")
graph.add_edge("process", END)

app = graph.compile()




## Conversation loop

conversation_history = []

if os.path.exists("conversation_history.txt"):

    with open("conversation_history.txt", 'r') as file:

        lines = file.readlines()
        
        for line in lines:

            if line.__contains__("human"):

                index = line.find(':') + 1
                conversation_history.append(HumanMessage(content=line[index:]))

            elif line.__contains__("AI"):

                index = line.find(':') + 1
                conversation_history.append(AIMessage(content=line[index:]))
    

user_input = input("Enter prompt: ")

while(user_input != "exit"):

    conversation_history.append(HumanMessage(content=user_input))

    response = app.invoke(AgentState(messages=conversation_history))

    conversation_history = response['messages']

    user_input = input("Enter prompt: ")

    if user_input == "exit":

        with open("conversation_history.txt", 'w') as file:

            for message in conversation_history:

                if isinstance(message, HumanMessage):

                    file.write(f"\nhuman: {message.content}")
                elif isinstance(message, AIMessage):

                    file.write(f"\nAI: {message.content}")