from agno.agent import Agent
from agno.models.openai import OpenAIChat,OpenAIResponses
from agno.models.google.gemini import Gemini
from agno.tools import tool
from agno.memory import Memory,AgentMemory
from agno.tools.reasoning import ReasoningTools
from agno.tools.duckduckgo import DuckDuckGoTools
from datetime import datetime
from dotenv import load_dotenv
import os
from agentes_agno.agente_banco_dados import AgenteBancoDados
from agentes_agno.agente_pesquisador import Pesquisador
from agentes_agno.agente_github import Agente_GitHub
from agno.team.team import Team  
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.storage.sqlite import SqliteStorage
from agno.tools.reasoning import ReasoningTools

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SMITHERY_API_KEY = os.getenv('SMITHERY_API_KEY')
GITHUB_ACCESS_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN')

print(GOOGLE_API_KEY, OPENAI_API_KEY, SMITHERY_API_KEY, GITHUB_ACCESS_TOKEN)

# Inicializar o banco de dados
sessoes = SqliteStorage(table_name="sessoes", db_file="Banco Agente.db" )
memorias = Memory(db=SqliteMemoryDb(table_name="memorias", db_file="memorias"))

AgentePrincipal = Team(
    memory=memorias,
    user_id="Leo",
    session_id="1",
    storage=sessoes,
    name='Agente Principal',
    role='Você é um agente principal que pode executar tarefas usando outros agentes e as suas ferramentas.',
    model=OpenAIChat(id='gpt-4o-mini', api_key=OPENAI_API_KEY),
    show_tool_calls=True,
    markdown=True,
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    num_history_runs=10,
    
    # CORREÇÃO: ReasoningTools vai em tools, não em members
    tools=[ReasoningTools(add_instructions=True, add_few_shot=True)],
    members=[AgenteBancoDados, Pesquisador, Agente_GitHub],  # Só agentes aqui
    
    mode='collaborate',
    debug_mode=True,
    show_members_responses=True,
    enable_user_memories=True,
    success_criteria='A resposta final deve ser clara, precisa e combinar as informações da internet (via Pesquisador), do GitHub (via Agente GitHub) e do banco de dados (via Agente de Banco de Dados) para resolver completamente a solicitação do usuário.'
)



if __name__ == "__main__":
    print("Agente Principal pronto. Digite 'sair' para encerrar.")
    while True:
        user_input = input("Você: ")
        if user_input.lower() == 'sair':
            break
        
        response = AgentePrincipal.print_response(user_input)