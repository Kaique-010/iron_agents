from typing import Dict, List
import re
import logging
import json
import os
from datetime import datetime
# Importações e registro dos agentes
from .base_agent import BaseAgent
from agents.banco_agent import banco_agent
from agents.django_agent import django_agent
from agents.react_agent import react_agent
from agents.doc_agent import doc_agent
from agents.architect_agent import architect_agent 

logger = logging.getLogger(__name__)

# Sistema de Memória/Contexto
class ConversationMemory:
    def __init__(self, memory_file='conversation_memory.json'):
        self.memory_file = memory_file
        self.conversations = self.load_memory()
        self.current_session = self.create_new_session()
    
    def load_memory(self):
        """Carrega memória de conversas do arquivo"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Erro ao carregar memória: {e}")
        return {'sessions': []}
    
    def save_memory(self):
        """Salva memória no arquivo"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversations, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar memória: {e}")
    
    def create_new_session(self):
        """Cria uma nova sessão de conversa"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session = {
            'id': session_id,
            'start_time': datetime.now().isoformat(),
            'interactions': [],
            'context': {}
        }
        return session
    
    def add_interaction(self, task, agent_used, result, files=None):
        """Adiciona uma interação à sessão atual"""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'task': task,
            'agent_used': agent_used,
            'result': result[:500] + '...' if len(result) > 500 else result,  # Limita tamanho
            'files': [f.name if hasattr(f, 'name') else str(f) for f in files] if files else []
        }
        self.current_session['interactions'].append(interaction)
        
        # Mantém apenas as últimas 10 interações por sessão
        if len(self.current_session['interactions']) > 10:
            self.current_session['interactions'] = self.current_session['interactions'][-10:]
        
        # Salva a sessão atual
        self.save_current_session()
    
    def save_current_session(self):
        """Salva a sessão atual na memória"""
        # Remove sessão anterior com mesmo ID se existir
        self.conversations['sessions'] = [s for s in self.conversations['sessions'] if s['id'] != self.current_session['id']]
        
        # Adiciona sessão atual
        self.conversations['sessions'].append(self.current_session.copy())
        
        # Mantém apenas as últimas 5 sessões
        if len(self.conversations['sessions']) > 5:
            self.conversations['sessions'] = self.conversations['sessions'][-5:]
        
        self.save_memory()
    
    def get_context_for_task(self, task):
        """Obtém contexto relevante para uma tarefa"""
        context = []
        
        # Adiciona interações recentes da sessão atual
        recent_interactions = self.current_session['interactions'][-3:]  # Últimas 3 interações
        for interaction in recent_interactions:
            context.append(f"Anterior: {interaction['task']} -> {interaction['result'][:200]}...")
        
        return "\n".join(context) if context else ""

# Instância global de memória
conversation_memory = ConversationMemory()

class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, name: str, agent_instance: BaseAgent):
        if name in self._agents:
            logger.warning(f"Agente '{name}' já registrado, sobrescrevendo.")
        self._agents[name] = agent_instance
        logger.info(f"Agente '{name}' registrado com sucesso.")
    
    def get_agent_names(self) -> list[str]:
        return list(self._agents.keys())
    
    def get_agent_instance(self, name: str) -> BaseAgent | None:
        agent_instance = self._agents.get(name)
        if agent_instance:
            return agent_instance
        return None

# Mapeamento de palavras-chave para agentes
AGENT_KEYWORDS = {
    'banco_agent': [
        'banco', 'database', 'sql', 'query', 'tabela', 'dados', 'crud',
        'insert', 'update', 'delete', 'select', 'postgresql', 'mysql'
    ],
    'django_agent': [
        'django', 'web', 'framework', 'views', 'models', 'urls', 'templates',
        'forms', 'admin', 'middleware', 'settings', 'migrate', 'runserver', 'api', 'viewsets', 'serializers', 'routers',
        'model', 'view', 'url', 'template', 'form', 'admin', 'middleware', 'settings', 'migrate', 'runserver', 'api', 'viewsets',
        'serializers', 'routers'
    ],
    'react_agent': [
        'react', 'frontend', 'componente', 'jsx', 'javascript', 'ui', 'interface',
        'estado', 'props', 'hooks', 'native', 'mobile', 'app', 'telas', 'navegação',
        'componente', 'estado', 'props', 'hooks', 'native', 'mobile', 'app', 'telas', 'navegação'
    ],
    'doc_agent': [
        'documentação', 'doc', 'readme', 'manual', 'guia', 'tutorial',
        'explicar', 'descrever', 'comentar', 'markdown', 'texto',
        'docstring', 'docstrings', 'análise', 'analisar', 'código',
        'arquivo', 'diretório', 'pasta', 'pdf', 'url', 'link',
        'processar', 'extrair', 'relatório', 'estatísticas'
    ],
    'arquiteto': [
        'arquitetura', 'design', 'estrutura', 'padrão', 'organização',
        'planejamento', 'sistema', 'projeto', 'blueprint', 'diagrama'
    ]
}

agent_registry = AgentRegistry()
agent_registry.register('banco_agent', banco_agent)
agent_registry.register('django_agent', django_agent)
agent_registry.register('react_agent', react_agent)
agent_registry.register('doc_agent', doc_agent)
agent_registry.register('arquiteto', architect_agent)

def find_best_agent(task: str) -> str:
    """Encontra o melhor agente baseado nas palavras-chave da tarefa"""
    task_lower = task.lower()
    agent_scores = {}
    
    # Calcula pontuação para cada agente baseado nas palavras-chave
    for agent_key, keywords in AGENT_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            # Conta ocorrências da palavra-chave na tarefa
            if keyword in task_lower:
                score += task_lower.count(keyword)
        agent_scores[agent_key] = score
    
    # Retorna o agente com maior pontuação
    best_agent = max(agent_scores, key=agent_scores.get)
    
    # Se nenhuma palavra-chave foi encontrada, usa o agente arquiteto como padrão
    if agent_scores[best_agent] == 0:
        logger.info(f"Nenhuma palavra-chave específica encontrada. Usando agente arquiteto.")
        return 'arquiteto'
    
    logger.info(f"Agente selecionado: '{best_agent}' com pontuação {agent_scores[best_agent]}")
    return best_agent

def orchestrate(task: str, agent_key: str = None, files=None):
    """Orquestra uma tarefa, selecionando automaticamente o agente se não especificado"""
    logger.info(f"Orquestrando tarefa: '{task}'")
    
    if not task:
        logger.warning("Tentativa de orquestrar com tarefa vazia.")
        return 'A tarefa não pode ser vazia.'
    
    # Obtém contexto das interações anteriores
    context = conversation_memory.get_context_for_task(task)
    
    # Se há contexto, adiciona à tarefa
    enhanced_task = task
    if context:
        enhanced_task = f"Contexto anterior:\n{context}\n\nTarefa atual: {task}"
        logger.info(f"Contexto adicionado à tarefa")
    
    # Se o agente não foi especificado, encontra o melhor automaticamente
    if not agent_key:
        agent_key = find_best_agent(task)
        logger.info(f"Agente selecionado automaticamente: '{agent_key}'")
    
    agent = agent_registry.get_agent_instance(agent_key)
    if not agent:
        logger.error(f"Agente '{agent_key}' não encontrado no registro.")
        return f'Agente {agent_key} não encontrado'
    
    try:
        result = agent.run(enhanced_task)
        
        # Salva a interação na memória
        conversation_memory.add_interaction(task, agent_key, result, files)
        
        logger.info(f"Agente '{agent_key}' executado com sucesso para a tarefa '{task}'.")
        return result
    except Exception as e:
        logger.exception(f"Erro ao executar o agente '{agent_key}' para a tarefa '{task}'.")
        error_msg = f'Ocorreu um erro ao executar o agente: {e}'
        
        # Salva o erro na memória também
        conversation_memory.add_interaction(task, agent_key, error_msg, files)
        
        return error_msg

def orchestrate_auto(task: str, files=None):
    """Versão simplificada que sempre seleciona o agente automaticamente"""
    return orchestrate(task, files=files)

time_de_agentes = [banco_agent, django_agent, react_agent, doc_agent, architect_agent]
