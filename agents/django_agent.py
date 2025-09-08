from core.base_agent import BaseAgent

django_agent = BaseAgent(
    name="Agente de Django",
    role="Você é um especialista em Django e Django Rest Framework. Ajude os usuários com bugs, melhores práticas e arquitetura de código.",
    model='openai',
)
