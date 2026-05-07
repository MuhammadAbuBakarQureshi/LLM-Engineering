import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_classic.memory import ConversationBufferMemory
from langchain_classic.chains import ConversationChain
from colorama import Fore, Style, init


# Initialize LLM

load_dotenv()

llm_model = "llama-3.3-70b-versatile"
GROQ_API = os.getenv('GROQ_API_KEY')
llm = ChatGroq(model=llm_model, api_key=GROQ_API, temperature=0.0)



# Define the output schema

bugs_schema = ResponseSchema(name="bugs",
                             description="any bugs or errors found in the code")

improvements_schema = ResponseSchema(name="improvements",
                                     description="suggestion to improve code")

rating_schema = ResponseSchema(name="rating",
                               description="a score out of 10")

summary_schema = ResponseSchema(name="summary",
                                description="a one line overall verdict")

code_schema = ResponseSchema(name="code",
                                description="Rewrite the code and return the code without bugs.")

response_schema = [bugs_schema,
                   improvements_schema,
                   rating_schema,
                   summary_schema,
                   code_schema]

parser = StructuredOutputParser.from_response_schemas(response_schema)

format_instructions = parser.get_format_instructions()



# Create prompt

prompt_template = """You are an expert code reviewer with deep knowledge of software engineering best practices, design patterns, and clean code principles. You will be given a piece of code and its intended purpose. Your job is to carefully analyze the code and provide honest, concise, and constructive feedback. Be specific — point out exact issues, not vague generalizations. Do not praise unnecessarily. If the code is bad, say so clearly. If it is good, say so briefly and focus on what can still be improved.
Purpose: {input}
code: {code}
{format_instructions}


IMPORTANT: In the "code" field, return the fixed code as a single line string. 
Replace every newline with the literal characters \\n"
Do not add markdown formatting anywhere in your response.
"""

prompt = ChatPromptTemplate.from_template(prompt_template)


# setup the memory and conversation chain

memory = ConversationBufferMemory()
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=False
)


## 


file_path = input("Enter file path: ")

with open(file_path, 'r') as file:

    code = file.read()


prompt_input = input("Enter the prompt here: ")


while(prompt_input != "exit"):

    message = message = prompt.format_messages(
        input=prompt_input,
        code=code,
        format_instructions=format_instructions
    )
    
    response = conversation.predict(input=message[0].content)

    response = parser.parse(response)

    init(autoreset=True)

    print(f"\n\n{Fore.RED}Bugs:{Fore.RESET} {response.get('bugs')}\n") if response.get('bugs') != None else ''

    print(f"{Fore.GREEN}Improvements:{Fore.RESET} {response.get('improvements')}\n") if response.get('improvements') != None else ''

    print(f"{Fore.YELLOW}Rating:{Fore.RESET} {response.get('rating')}\n") if response.get('rating') != None else ''

    print(f"{Fore.LIGHTBLACK_EX}Summary:{Fore.RESET} {response.get('rating')}\n") if response.get('summary') != None else ''

    print(f"{Fore.LIGHTBLACK_EX}Code:{Fore.RESET} {response.get('code')}") if response.get('code') != None else ''

    write_check = input(f"{Fore.GREEN}\n\nDo you want to replace the new code [Y/N]: {Fore.RESET}")

    if (write_check == "yes") or (write_check == "y") :

        with open(file_path , 'w') as file:

            file.write(response.get('code'))
    
        with open(file_path, 'r') as file:

            code = file.read()

    print(f"\n\n")

    print(os.get_terminal_size().columns * "-")

    prompt_input = input("\n\nEnter the prompt here: ")