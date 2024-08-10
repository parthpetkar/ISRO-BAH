from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from .models import Chat
from .serializers import ChatSerializer

@api_view(['GET'])
def list_chats(request):
    chats = Chat.objects.all().order_by('-created_at')
    serializer = ChatSerializer(chats, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def save_chat(request):
    serializer = ChatSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def save_chat_to_cache(request):
    chat_data = request.data.get('chat_data')
    cache.set('current_chat', chat_data)
    return Response({"status": "chat saved to cache"}, status=status.HTTP_200_OK)

@api_view(['POST'])
def save_cache_to_db(request):
    chat_data = cache.get('current_chat')
    chat_id = request.data.get('chat_id', None)
    
    if not chat_data:
        return Response({"status": "no chat found in cache"}, status=status.HTTP_400_BAD_REQUEST)
    
    if chat_id:
        try:
            chat = Chat.objects.get(id=chat_id)
            chat.input_response_pairs = chat_data
            chat.save()
        except Chat.DoesNotExist:
            return Response({"error": "Chat not found"}, status=status.HTTP_404_NOT_FOUND)
    else:
        # Create a new chat if chat_id is not provided
        chat = Chat.objects.create(input_response_pairs=chat_data)
        chat_id = chat.id

    cache.delete('current_chat')
    return Response({"status": "chat saved to db", "chat_id": chat_id}, status=status.HTTP_200_OK)

    chat_data = cache.get('current_chat')
    chat_id = request.data.get('chat_id')
    if chat_data and chat_id:
        try:
            chat = Chat.objects.get(id=chat_id)
            chat.input_response_pairs = chat_data
            chat.save()
        except Chat.DoesNotExist:
            Chat.objects.create(input_response_pairs=chat_data)
        cache.delete('current_chat')
        return Response({"status": "chat saved to db"}, status=status.HTTP_200_OK)
    return Response({"status": "no chat found in cache"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def fetch_chat_from_db(request, chat_id):
    try:
        chat = Chat.objects.get(id=chat_id)
        return Response(chat.input_response_pairs, status=status.HTTP_200_OK)
    except Chat.DoesNotExist:
        return Response({"error": "Chat not found"}, status=status.HTTP_404_NOT_FOUND)
