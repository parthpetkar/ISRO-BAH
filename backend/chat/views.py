from django.core.cache import cache
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Chat
from .serializers import ChatSerializer

@api_view(['POST'])
def save_chat_to_cache(request):
    chat_data = request.data.get('chat_data', [])
    cache.set('current_chat', chat_data)
    return Response({"message": "Chat saved to cache"}, status=status.HTTP_200_OK)

@api_view(['POST'])
def save_cache_to_db(request):
    chat_data = cache.get('current_chat')
    if chat_data:
        serializer = ChatSerializer(data={'input_response_pairs': chat_data})
        if serializer.is_valid():
            serializer.save()
            cache.delete('current_chat')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "No chat data in cache"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def fetch_chat_from_db(request, chat_id):
    try:
        chat = Chat.objects.get(pk=chat_id)
        cache.set('current_chat', chat.input_response_pairs)
        return Response(chat.input_response_pairs, status=status.HTTP_200_OK)
    except Chat.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
def list_chats(request):
    chats = Chat.objects.all().order_by('-created_at')
    serializer = ChatSerializer(chats, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
