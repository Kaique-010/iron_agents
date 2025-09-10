from dotenv import load_dotenv
load_dotenv()
import os
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from textwrap import dedent

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SMITHERY_API_KEY = os.getenv('SMITHERY_API_KEY')

Pesquisador = Agent(
    name='Pesquisador',
    model=OpenAIChat(id='gpt-4o-mini', api_key=OPENAI_API_KEY),
    tools=[DuckDuckGoTools],
    role="Pesquisador de temas em geral baseado na pergunta",
    add_name_to_instructions=True,
    instructions=dedent('''
    Você é um pesquisador experiente.
    Use a ferramenta DuckDuckGo para buscar informações.
    '''),
    markdown=True)
