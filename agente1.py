from agno.agent import Agent
from agno.models.openai import OpenAIChat,OpenAIResponses
from agno.models.google.gemini import Gemini
from agno.tools import tool
from agno.tools.reasoning import ReasoningTools
from agno.tools.duckduckgo import DuckDuckGoTools
from datetime import datetime
from dotenv import load_dotenv
import os


load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SMITHERY_API_KEY = os.getenv('SMITHERY_API_KEY')
print(GOOGLE_API_KEY, OPENAI_API_KEY, SMITHERY_API_KEY)


agente_principal = Agent(
    name='Agente Principal',
    role='Você é um agente principal que pode executar tarefas usando outros agentes e as suas ferramentas.',
    model=OpenAIChat(id='gpt-4o-mini', api_key=OPENAI_API_KEY),
    show_tool_calls=True,
    markdown=True,
    tools=[ReasoningTools, DuckDuckGoTools],
    add_datetime_to_instructions=True,
    memory=True,
)



if __name__ == "__main__":
    print("Agente Principal pronto. Digite 'sair' para encerrar.")
    while True:
        user_input = input("Você: ")
        if user_input.lower() == 'sair':
            break
        
        response = agente_principal.print_response(user_input)
