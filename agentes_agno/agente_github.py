from dotenv import load_dotenv
load_dotenv()
import os
from agno.agent import Agent
from agno.models.openai import OpenAIChat,OpenAIResponses
from agno.tools.github import GithubTools
from textwrap import dedent

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
Agente_GitHub = Agent(
    name='Agente GitHub',
    role='Você é um agente especialista em GitHub que pode executar tarefas usando as ferramentas do GitHub.',
    model=OpenAIChat(id='gpt-4o-mini', api_key=OPENAI_API_KEY),
    show_tool_calls=True,
    markdown=True,
    add_datetime_to_instructions=True,
    tools=[GithubTools()],  # Sem parênteses extras
    debug_mode=True,
    instructions=dedent("""
        1. Quando perguntado sobre repositórios, sempre especifique o owner/repo_name no formato correto
        2. Para listar pull requests, use: list_pull_requests com owner e repo_name
        3. Para obter detalhes do repositório, use: get_repository com owner e repo_name
        4. Exemplo: para agno-agi/agno, owner='agno-agi' e repo_name='agno'
        5. Sempre pergunte qual repositório o usuário quer analisar se não for especificado
    """)
)