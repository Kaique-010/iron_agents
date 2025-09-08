import os
import sys
import inspect
import importlib.util
import ast
from pathlib import Path
from typing import List, Dict, Any
import json
from urllib.parse import urlparse
import urllib.request
from core.base_agent import BaseAgent

class DocAgent(BaseAgent):
    """
    Agente especializado em processamento de documentação usando docstrings Python.
    Pode processar arquivos Python, diretórios e URLs para extrair documentação.
    """
    
    def __init__(self):
        super().__init__(
            name="Doc Agent",
            role="Especialista em análise de documentação e docstrings Python",
            model="openai"
        )
    
    def run(self, prompt: str) -> str:
        """
        Sobrescreve o método run do BaseAgent para usar nossa lógica personalizada.
        
        Args:
            prompt (str): Prompt/tarefa a ser processada
            
        Returns:
            str: Resultado do processamento
        """
        return self.process_task(prompt)
    
    def process_task(self, task: str) -> str:
        """
        Processa tarefas relacionadas à documentação.
        
        Args:
            task (str): Descrição da tarefa de documentação
            
        Returns:
            str: Resultado do processamento da documentação
        """
        try:
            # Identifica o tipo de tarefa
            if "pdf" in task.lower():
                return self._process_pdf_request(task)
            elif "url" in task.lower() or "http" in task.lower():
                return self._process_url_request(task)
            elif "diretório" in task.lower() or "pasta" in task.lower() or "directory" in task.lower():
                return self._process_directory_request(task)
            elif "arquivo" in task.lower() or "file" in task.lower():
                return self._process_file_request(task)
            else:
                return self._analyze_docstrings_in_project()
                
        except Exception as e:
            return f"Erro ao processar documentação: {str(e)}"
    
    def _process_pdf_request(self, task: str) -> str:
        """
        Processa solicitações relacionadas a PDFs.
        """
        return "📄 Processamento de PDF não implementado ainda. Use arquivos Python (.py) para análise de docstrings."
    
    def _process_url_request(self, task: str) -> str:
        """
        Processa URLs para extrair código Python e analisar docstrings.
        """
        try:
            # Extrai URLs da tarefa
            words = task.split()
            urls = [word for word in words if word.startswith(('http://', 'https://'))]
            
            if not urls:
                return "❌ Nenhuma URL válida encontrada na tarefa."
            
            results = []
            for url in urls:
                try:
                    # Baixa o conteúdo da URL
                    with urllib.request.urlopen(url) as response:
                        content = response.read().decode('utf-8')
                    
                    # Se for um arquivo Python, analisa as docstrings
                    if url.endswith('.py'):
                        docstrings = self._extract_docstrings_from_content(content, url)
                        results.append(f"🌐 **URL**: {url}\n{docstrings}")
                    else:
                        results.append(f"🌐 **URL**: {url}\n📝 Conteúdo baixado ({len(content)} caracteres)")
                        
                except Exception as e:
                    results.append(f"❌ Erro ao processar {url}: {str(e)}")
            
            return "\n\n".join(results)
            
        except Exception as e:
            return f"❌ Erro ao processar URLs: {str(e)}"
    
    def _process_directory_request(self, task: str) -> str:
        """
        Processa diretórios para analisar docstrings de arquivos Python.
        """
        try:
            # Extrai caminhos de diretório da tarefa
            words = task.split()
            directories = []
            
            for word in words:
                if os.path.isdir(word):
                    directories.append(word)
                elif '\\' in word or '/' in word:
                    # Tenta interpretar como caminho
                    if os.path.isdir(word):
                        directories.append(word)
            
            if not directories:
                # Se não encontrou diretórios específicos, usa o diretório atual
                directories = [os.getcwd()]
            
            results = []
            for directory in directories:
                result = self._analyze_directory_docstrings(directory)
                results.append(f"📁 **Diretório**: {directory}\n{result}")
            
            return "\n\n".join(results)
            
        except Exception as e:
            return f"❌ Erro ao processar diretórios: {str(e)}"
    
    def _process_file_request(self, task: str) -> str:
        """
        Processa arquivos específicos para análise de código.
        """
        try:
            # Extrai nomes de arquivos da tarefa
            words = task.split()
            files = []
            
            # Extensões suportadas
            supported_extensions = ['.py', '.js', '.jsx', '.ts', '.tsx']
            
            for word in words:
                # Verifica se é um arquivo existente com extensão suportada
                if os.path.isfile(word) and any(word.endswith(ext) for ext in supported_extensions):
                    files.append(word)
                # Tenta encontrar o arquivo no projeto
                elif any(word.endswith(ext) for ext in supported_extensions):
                    for root, dirs, filenames in os.walk(os.getcwd()):
                        if word in filenames:
                            files.append(os.path.join(root, word))
            
            if not files:
                return "❌ Nenhum arquivo de código válido encontrado na tarefa. Suporto: .py, .js, .jsx, .ts, .tsx"
            
            results = []
            for file_path in files:
                if file_path.endswith('.py'):
                    result = self._analyze_file_docstrings(file_path)
                else:
                    result = self._analyze_js_file(file_path)
                results.append(f"📄 **Arquivo**: {file_path}\n{result}")
            
            return "\n\n".join(results)
            
        except Exception as e:
            return f"❌ Erro ao processar arquivos: {str(e)}"
    
    def _analyze_docstrings_in_project(self) -> str:
        """
        Analisa todas as docstrings no projeto atual.
        """
        try:
            project_root = os.getcwd()
            return self._analyze_directory_docstrings(project_root)
        except Exception as e:
            return f"❌ Erro ao analisar projeto: {str(e)}"
    
    def _analyze_directory_docstrings(self, directory: str) -> str:
        """
        Analisa docstrings em todos os arquivos Python de um diretório.
        """
        results = []
        python_files = []
        
        # Encontra todos os arquivos Python
        for root, dirs, files in os.walk(directory):
            # Ignora diretórios comuns que não precisam de análise
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv', 'env', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        if not python_files:
            return "❌ Nenhum arquivo Python encontrado no diretório."
        
        # Analisa cada arquivo
        total_functions = 0
        total_classes = 0
        documented_functions = 0
        documented_classes = 0
        
        for file_path in python_files[:10]:  # Limita a 10 arquivos para não sobrecarregar
            try:
                file_result = self._analyze_file_docstrings(file_path)
                if "Funções:" in file_result:
                    # Conta estatísticas básicas
                    lines = file_result.split('\n')
                    for line in lines:
                        if "✅" in line and "def " in line:
                            documented_functions += 1
                            total_functions += 1
                        elif "❌" in line and "def " in line:
                            total_functions += 1
                        elif "✅" in line and "class " in line:
                            documented_classes += 1
                            total_classes += 1
                        elif "❌" in line and "class " in line:
                            total_classes += 1
                
                results.append(f"**{os.path.basename(file_path)}**\n{file_result}")
            except Exception as e:
                results.append(f"❌ Erro ao analisar {file_path}: {str(e)}")
        
        # Adiciona estatísticas gerais
        stats = f"""📊 **Estatísticas de Documentação**
📁 Arquivos analisados: {len(results)}
🔧 Funções documentadas: {documented_functions}/{total_functions}
🏗️ Classes documentadas: {documented_classes}/{total_classes}
📈 Taxa de documentação: {((documented_functions + documented_classes) / max(total_functions + total_classes, 1) * 100):.1f}%
"""
        
        return stats + "\n\n" + "\n\n".join(results)
    
    def _analyze_file_docstrings(self, file_path: str) -> str:
        """
        Analisa docstrings em um arquivo Python específico.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self._extract_docstrings_from_content(content, file_path)
            
        except Exception as e:
            return f"❌ Erro ao ler arquivo: {str(e)}"
    
    def _analyze_js_file(self, file_path: str) -> str:
        """
        Analisa arquivos JavaScript/TypeScript e fornece sugestões de melhorias.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Análise básica do código JavaScript
            lines = content.split('\n')
            total_lines = len(lines)
            
            # Contadores para análise
            functions_count = 0
            components_count = 0
            comments_count = 0
            todos_count = 0
            
            # Sugestões de melhorias
            suggestions = []
            
            for i, line in enumerate(lines, 1):
                line_stripped = line.strip()
                
                # Conta funções
                if 'function ' in line or '=>' in line or 'const ' in line and '=>' in line:
                    functions_count += 1
                
                # Conta componentes React
                if 'export default' in line or 'const ' in line and 'React' in content:
                    components_count += 1
                
                # Conta comentários
                if line_stripped.startswith('//') or line_stripped.startswith('/*'):
                    comments_count += 1
                
                # Conta TODOs
                if 'TODO' in line.upper() or 'FIXME' in line.upper():
                    todos_count += 1
                    suggestions.append(f"📝 Linha {i}: TODO/FIXME encontrado - {line_stripped}")
                
                # Verifica console.log em produção
                if 'console.log' in line:
                    suggestions.append(f"⚠️ Linha {i}: console.log encontrado - considere remover em produção")
                
                # Verifica funções muito longas (mais de 50 linhas)
                if 'function ' in line or ('=>' in line and 'const' in line):
                    # Conta linhas até próxima função ou fim do arquivo
                    func_lines = 0
                    for j in range(i, min(i + 60, total_lines)):
                        if j < len(lines) and ('}' in lines[j] and lines[j].count('}') >= lines[j].count('{')):
                            break
                        func_lines += 1
                            
                    if func_lines > 50:
                        suggestions.append(f"📏 Linha {i}: Função muito longa ({func_lines} linhas) - considere dividir")
            
            # Verifica estrutura geral
            if comments_count / total_lines < 0.1:
                suggestions.append("📚 Poucos comentários no código - considere adicionar mais documentação")
            
            if 'import' not in content and 'require' not in content:
                suggestions.append("📦 Nenhuma importação encontrada - verifique se o arquivo está completo")
            
            # Sugestões específicas para React
            if 'React' in content or 'jsx' in file_path.lower():
                if 'useState' in content and 'useEffect' not in content:
                    suggestions.append("⚛️ Usando useState sem useEffect - verifique se precisa de efeitos colaterais")
                
                if 'key=' not in content and '.map(' in content:
                    suggestions.append("🔑 Renderização de listas sem key - adicione propriedade key nos elementos")
            
            # Monta o resultado
            result = f"""📊 **Estatísticas do Arquivo**:
- Total de linhas: {total_lines}
- Funções encontradas: {functions_count}
- Componentes: {components_count}
- Comentários: {comments_count}
- TODOs pendentes: {todos_count}

"""
            
            if suggestions:
                result += "🔧 **Sugestões de Melhorias**:\n"
                for suggestion in suggestions[:10]:  # Limita a 10 sugestões
                    result += f"- {suggestion}\n"
                
                if len(suggestions) > 10:
                    result += f"... e mais {len(suggestions) - 10} sugestões\n"
            else:
                result += "✅ **Código parece estar bem estruturado!**\n"
            
            return result
            
        except Exception as e:
            return f"❌ Erro ao analisar arquivo JavaScript: {str(e)}"
    
    def _extract_docstrings_from_content(self, content: str, source_name: str) -> str:
        """
        Extrai docstrings do conteúdo de um arquivo Python.
        """
        try:
            tree = ast.parse(content)
            
            functions = []
            classes = []
            module_docstring = ast.get_docstring(tree)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    docstring = ast.get_docstring(node)
                    status = "✅" if docstring else "❌"
                    functions.append(f"{status} def {node.name}(): {docstring[:100] if docstring else 'Sem documentação'}")
                
                elif isinstance(node, ast.ClassDef):
                    docstring = ast.get_docstring(node)
                    status = "✅" if docstring else "❌"
                    classes.append(f"{status} class {node.name}: {docstring[:100] if docstring else 'Sem documentação'}")
            
            result = []
            
            if module_docstring:
                result.append(f"📋 **Documentação do Módulo:**\n{module_docstring}")
            
            if classes:
                result.append(f"🏗️ **Classes ({len(classes)}):**\n" + "\n".join(classes))
            
            if functions:
                result.append(f"🔧 **Funções ({len(functions)}):**\n" + "\n".join(functions))
            
            if not classes and not functions:
                result.append("📝 Nenhuma classe ou função encontrada.")
            
            return "\n\n".join(result)
            
        except SyntaxError as e:
            return f"❌ Erro de sintaxe no arquivo: {str(e)}"
        except Exception as e:
            return f"❌ Erro ao processar conteúdo: {str(e)}"

# Instância do agente
doc_agent = DocAgent()
