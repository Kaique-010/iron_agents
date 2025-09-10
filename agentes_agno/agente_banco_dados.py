from dotenv import load_dotenv
load_dotenv()
import os
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.postgres import PostgresTools
from agno.tools.visualization import VisualizationTools
from textwrap import dedent

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SMITHERY_API_KEY = os.getenv('SMITHERY_API_KEY')

# 1. Puxe a URL de conexão do seu arquivo .env
DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_PORT = os.getenv('DATABASE_PORT')
DATABASE_NAME = os.getenv('DATABASE_NAME')
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')

postgres_tools = PostgresTools(
    host=DATABASE_HOST,
    port=DATABASE_PORT,
    db_name=DATABASE_NAME,
    user=DATABASE_USER,
    password=DATABASE_PASSWORD
)

AgenteBancoDados = Agent(
    name='Agente de Banco de Dados',
    model=OpenAIChat(id='gpt-4o-mini', api_key=OPENAI_API_KEY),
    tools=[postgres_tools,VisualizationTools(output_dir="my_charts")],
    show_tool_calls=True,
    add_datetime_to_instructions=True,
    memory=True,
    role="Agente de banco de dados",
    add_name_to_instructions=True,
    instructions=dedent('''
    Você é um agente de banco de dados.
    Use as ferramentas SQL e Postgres para buscar informações.
    Seja bem-vindo ao agente de banco de dados.
    Responda as perguntas do usuário de forma clara e concisa.
    Use as ferramentas SQL e Postgres para buscar informações.
    Seja respeitoso e não ofensivo.
    Responda apenas as perguntas relacionadas ao banco de dados.
    Seja sempre útil e forneça informações precisas.
    Insights sobre as consultas SQL e Postgres.
    Use as ferramentas de visualização para criar gráficos referente as consultas.
    '''),
    markdown=True)