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

            return f"Document has been saved successfully to {filename}"

    except Exception as e:

        return f"Error saving document: {e}"
    

tools = [update,
        save]



llm_name = "llama-3.3-70b-versatile"
llm = ChatGroq(model=llm_name).bind_tools(tools)



def agent(state: AgentState) -> AgentState:

    system_prompt = SystemMessage(
        content = f"""
        You are Drafter, a helpful writing assistant. You are going to help the user update and modify documents

        - If the user wants to updater or modify content, use the 'update' tool with the complete updated content
        - If the user wants to save and finish, you need to use the 'save' tool.
        - Make sure to always show the current document state after modifications.

        The current document content is: {document_content}
        """
    )

    if not state['messages']:

        user_input = "I want to create and edit a document, can you help me?"
        user_message = HumanMessage(content=user_input)

    else:

        user_input = input("\nWhat would you like to do with the doucment: ")
        print(f"\n👤 USER: {user_input}")
        user_message = HumanMessage(content=user_input)

    all_messages = [system_prompt] + list(state['messages']) + [user_message]

    response = llm.invoke(all_messages)

    print("\n🤖 AI:{response.content}")

    if hasattr(response, "tool_calls") and response.tool_calls:

        print(f"\n🔧 Using Tools: {[ tc['name'] for tc in response.tool_calls]}")

    return {"messages" : [user_message, response]}


def should_continue(state: AgentState):
    """Determine if we should continue or end the conversation"""

    if not state['messages']:

        return "continue"