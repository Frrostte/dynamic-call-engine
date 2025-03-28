from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import F
from .models import Conversation, Message
from campaigns.models import Campaign
from .utils import generate_bot_response
import logging

logger = logging.getLogger(__name__)

@login_required
def chatbot_view(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id, user=request.user)
    return render(request, 'chatbot/chatbot.html', {'campaign': campaign})


@login_required
def chatbot_message(request, campaign_id):
    if request.method == 'POST':
        try:
            campaign = get_object_or_404(Campaign, id=campaign_id, user=request.user)
            user_message = request.POST.get('message')
            
            conversation, created = Conversation.objects.get_or_create(
                user=request.user,
                campaign=campaign,
                end_time__isnull=True
            )
            
            Message.objects.create(conversation=conversation, content=user_message, is_bot=False)
            
            conversation_history = Message.objects.filter(conversation=conversation).order_by('timestamp')
            bot_message = generate_bot_response(campaign, user_message, conversation_history)
                    
            Message.objects.create(conversation=conversation, content=bot_message, is_bot=True)
            
            # Increment the chatbot interactions count
            campaign.chatbot_interactions = F('chatbot_interactions') + 1
            campaign.save()
        
            return JsonResponse({'message': bot_message.replace("\n", " ").strip()})
        except Exception as e:
            logger.error(f"Failed to process message: {str(e)}")
            return JsonResponse({'error': 'Failed to process your message, please try again later.'}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)



@login_required
def chat_history(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id, user=request.user)
    conversation = Conversation.objects.filter(user=request.user, campaign=campaign).last()
    
    if conversation:
        messages = Message.objects.filter(conversation=conversation).order_by('timestamp')
        data = {
            'messages': [
                {'content': msg.content, 'is_bot': msg.is_bot, 'timestamp': msg.timestamp.isoformat()}
                for msg in messages
            ]
        }
    else:
        # add the pitch into the conversation as first message to start the conversation
        start_message = campaign.starting_pitch if campaign.starting_pitch else "Hello! How can I help you today?"
        conversation, created = Conversation.objects.get_or_create(user=request.user, campaign=campaign)
        message = Message.objects.create(conversation=conversation, content=start_message, is_bot=True)
        data = {
            'messages': [
                {'content': message.content, 'is_bot': message.is_bot, 'timestamp': message.timestamp.isoformat()}
            ]
        }
        
    return JsonResponse(data)
