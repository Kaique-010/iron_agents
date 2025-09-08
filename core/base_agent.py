from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.google.gemini import Gemini
from dotenv import load_dotenv
import os
import time
import random
from typing import Any

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SMITHERY_API_KEY = os.getenv('SMITHERY_API_KEY')
print(GOOGLE_API_KEY, OPENAI_API_KEY, SMITHERY_API_KEY)

class BaseAgent:
    def __init__(self, name, role, model='openai'):
        if model=='openai':
            # Usa gpt-4o-mini por padrão (mais econômico)
            model_id = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
            llm = OpenAIChat(id=model_id, api_key=OPENAI_API_KEY)
        elif model=='gemini':
            # Usa gemini-1.5-flash por padrão (mais econômico)
            model_id = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
            llm = Gemini(id=model_id, api_key=GOOGLE_API_KEY)
        else:
            raise ValueError('Modelo inválido')

        self.agent = Agent(name=name, role=role, model=llm, show_tool_calls=True, markdown=True, memory=True)
        self.name = name
        self.role = role

    def run(self, prompt: str, max_retries: int = 3) -> str:
        """Executa o prompt com retry automático para erros de rate limiting"""
        for attempt in range(max_retries + 1):
            try:
                response = self.agent.run(prompt)
                # Extrair apenas o conteúdo de texto da resposta
                if hasattr(response, 'content'):
                    return response.content
                elif hasattr(response, 'text'):
                    return response.text
                else:
                    return str(response)
            except Exception as e:
                error_str = str(e)
                
                # Verifica se é erro 429 (Too Many Requests)
                if '429' in error_str or 'Too Many Requests' in error_str:
                    if attempt < max_retries:
                        # Backoff exponencial com jitter
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        print(f"Rate limit atingido. Tentativa {attempt + 1}/{max_retries + 1}. Aguardando {wait_time:.1f}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return f"❌ Erro de rate limit após {max_retries + 1} tentativas. Tente novamente em alguns minutos."
                
                # Para outros erros, retorna imediatamente
                return f"❌ Erro ao executar agente: {error_str}"
        
        return "❌ Erro inesperado no sistema de retry"
    
    def get_memory_summary(self) -> str:
        """Retorna um resumo da memória do agente"""
        if hasattr(self.agent, 'memory') and self.agent.memory:
            # Tenta acessar as mensagens da memória
            if hasattr(self.agent.memory, 'messages'):
                recent_messages = self.agent.memory.messages[-5:]  # Últimas 5 mensagens
                return f"Contexto recente do {self.name}: {len(recent_messages)} interações na memória"
            return f"Memória ativa para {self.name}"
        return f"Sem memória persistente para {self.name}"
    
    def clear_memory(self):
        """Limpa a memória do agente"""
        if hasattr(self.agent, 'memory') and self.agent.memory:
            if hasattr(self.agent.memory, 'clear'):
                self.agent.memory.clear()
            elif hasattr(self.agent.memory, 'messages'):
                self.agent.memory.messages.clear()
    
    def add_context_to_prompt(self, prompt: str, context: str = None) -> str:
        """Adiciona contexto ao prompt se fornecido"""
        if context:
            return f"Contexto anterior:\n{context}\n\nTarefa atual: {prompt}"
        return prompt
    
    def __str__(self):
        return self.agent.name