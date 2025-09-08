from django.urls import path, include
from django.shortcuts import redirect
from agents import views

urlpatterns = [
    path('', lambda request: redirect('agents/ui/', permanent=False)),
    path('agents/ui/', views.agents_ui, name='agents_ui'),
    path('agents/run/', views.run_agent, name='run_agent'),
    path('agents/auto/', views.run_agent_auto, name='run_agent_auto'),
    path('agents/upload/', views.upload_and_analyze, name='upload_and_analyze'),
]
