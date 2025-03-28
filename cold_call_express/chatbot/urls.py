from django.urls import path
from .views import chatbot_view, chatbot_message, chat_history

app_name = 'chatbot'

urlpatterns = [
    path('<int:campaign_id>/', chatbot_view, name='chatbot_view'),
    path('<int:campaign_id>/message/', chatbot_message, name='chatbot_message'),
    path('<int:campaign_id>/history/', chat_history, name='chat_history'),
]