import os

from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, SystemMessage, ToolMessage, HumanMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from IPython.display import display, Image


load_dotenv("../../.env")

document_content = ""


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


@tool
def update(content: str) -> str:
    """update the document with the provided content"""

    global document_content
    document_content = content

    if document_content:

        print(f"\n📃 Updated Document: {document_content}")

    return document_content

@tool
def save(filename: str) -> str:
    """save the content in the text file and finish the process
    
    Args:
        filename: Name of the text file.

    """

    try:

        with open(filename, 'w') as file:
            
            global document_content
            file.write(document_content)

            print(f"\n🗄️ Document has been saved successfully to {filename}")
            return f"\n🗄️ Document has been saved successfully to {filename}"

    except Exception as e:

        print(f"\n🌋 Error saving document: {e}")
        return f"\n🌋 Error saving document: {e}"
    

tools = [update,
        save]



llm_name = "llama-3.3-70b-versatile"
llm = ChatGroq(model=llm_name).bind_tools(tools)



def agent(state: AgentState) -> AgentState:

    system_prompt = SystemMessage(
        content = f"""
        You are Drafter, a helpful writing assistant. You are going to help the user update and modify documents

        - When writing content, use proper line breaks and paragraphs for readability
        - If the user wants to updater or modify content, use the 'update' tool with the complete updated content
        - If the user wants to save and finish, you need to use the 'save' tool.
        - Make sure to always show the current document state after modifications.c

        The current document content is: {document_content}
        """
    )

    print(f"\n{os.get_terminal_size().columns * "="}\n")

    if not state['messages']:

        user_input = "I want to create and edit a document, can you help me?"
        user_message = HumanMessage(content=user_input)

    else:

        user_input = input("\nWhat would you like to do with the doucment: ")
        print(f"\n👤 USER: {user_input}")
        user_message = HumanMessage(content=user_input)

    all_messages = [system_prompt] + list(state['messages']) + [user_message]

    response = llm.invoke(all_messages)

    print(f"\n🤖 AI:{response.content}")

    if hasattr(response, "tool_calls") and response.tool_calls:

        print(f"\n🔧 Using Tools: {[ tc['name'] for tc in response.tool_calls]}")

    return {"messages" : [user_message, response]}


def should_continue(state: AgentState):
    """Determine if we should continue or end the conversation"""

    if not state['messages']:

        return "continue"
    
    for message in reversed(state['messages']):

        if((isinstance(message, ToolMessage)) and
        "saved" in message.content.lower() and
        "document" in message.content.lower()):
            
            return "end"
        
    return "continue"


graph = StateGraph(AgentState)


graph.add_node("agent", agent)
graph.add_node("tools", ToolNode(tools=tools))

graph.add_edge(START, "agent")
graph.add_edge("agent", "tools")

graph.add_conditional_edges(
    "tools",
    should_continue,
    
    {
        "continue": "agent",
        "end": END
    }
)

app = graph.compile()

def print_title(title):

    columns = os.get_terminal_size().columns
    half_screen = columns // 2 

    space_around_title = 4
    title_len = len(title) // 2 + space_around_title
    penalty = 0

    content_len = ((half_screen*2) - (title_len*2)) + (space_around_title*2) + (len(title))

    if not content_len <= columns: penalty = content_len - columns
                
    print(f"\n{(half_screen - title_len) * "="}{space_around_title * ' '}{title.upper()}{space_around_title * ' '}{(half_screen - title_len - penalty) * "="}\n\n" )

print_title("drafter")

try:

    response = app.invoke(AgentState(messages=[]), stream_mode="values")

except Exception as e:

    print(f"Error: {e}")

print_title("drafter finished")