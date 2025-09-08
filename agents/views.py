from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import os
import tempfile
from core.orchestrator import orchestrate, orchestrate_auto, agent_registry


def agents_ui(request):
    return render(request, 'console.html')

@csrf_exempt
def run_agent(request):
    if request.method == 'POST':
        task = request.POST.get('task', '')
        agent = request.POST.get('agent', '')
        
        if not task:
            return JsonResponse({'error': 'Tarefa não pode ser vazia'}, status=400)
        
        # Se nenhum agente foi especificado, usa seleção automática
        if not agent or agent == 'auto':
            result = orchestrate_auto(task)
            return JsonResponse({'result': result, 'agent_used': 'auto-selected'})
        
        # Validação do agente especificado
        agent_names = agent_registry.get_agent_names()
        if agent not in agent_names:
            return JsonResponse({'error': 'Agente inválido'}, status=400)
        
        result = orchestrate(task, agent)
        return JsonResponse({'result': result, 'agent_used': agent})

@csrf_exempt
def run_agent_auto(request):
    """Endpoint dedicado para seleção automática de agentes"""
    if request.method == 'POST':
        task = request.POST.get('task', '')
        
        if not task:
            return JsonResponse({'error': 'Tarefa não pode ser vazia'}, status=400)
        
        result = orchestrate_auto(task)
        return JsonResponse({'result': result, 'mode': 'auto-selection'})

@csrf_exempt
def upload_and_analyze(request):
    """Endpoint para upload de arquivos e análise com doc_agent"""
    if request.method == 'POST':
        uploaded_files = request.FILES.getlist('files')
        directory_path = request.POST.get('directory_path', '')
        
        if not uploaded_files and not directory_path:
            return JsonResponse({'error': 'Nenhum arquivo ou diretório especificado'}, status=400)
        
        results = []
        
        # Processa arquivos enviados
        if uploaded_files:
            for uploaded_file in uploaded_files:
                if uploaded_file.name.endswith('.py'):
                    try:
                        # Salva temporariamente o arquivo
                        with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as temp_file:
                            content = uploaded_file.read().decode('utf-8')
                            temp_file.write(content)
                            temp_file_path = temp_file.name
                        
                        # Analisa com doc_agent
                        task = f"analisar arquivo {temp_file_path}"
                        result = orchestrate(task, 'doc_agent', files=[uploaded_file])
                        results.append({
                            'file': uploaded_file.name,
                            'analysis': result
                        })
                        
                        # Remove arquivo temporário
                        os.unlink(temp_file_path)
                        
                    except Exception as e:
                        results.append({
                            'file': uploaded_file.name,
                            'error': f'Erro ao processar: {str(e)}'
                        })
                else:
                    results.append({
                        'file': uploaded_file.name,
                        'error': 'Apenas arquivos Python (.py) são suportados'
                    })
        
        # Processa diretório especificado
        if directory_path and os.path.isdir(directory_path):
            try:
                task = f"analisar diretório {directory_path}"
                result = orchestrate(task, 'doc_agent', files=None)
                results.append({
                    'directory': directory_path,
                    'analysis': result
                })
            except Exception as e:
                results.append({
                    'directory': directory_path,
                    'error': f'Erro ao processar diretório: {str(e)}'
                })
        
        return JsonResponse({
            'results': results,
            'total_processed': len(results)
        })
