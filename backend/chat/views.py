import requests
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
    
    if not chat_data:
        return Response({"status": "No chat data provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Assuming the user input is the last item in the chat_data list
    user_input = chat_data[-1].get('text')
    
    try:
        # Send the user input to the first API
        external_api_url = "http://127.0.0.1:5000/api/retrieve"  # Replace with your first API URL
        response = requests.post(external_api_url, json={"query": user_input})
        response.raise_for_status()  # Raise an error for bad HTTP responses
        response_data = response.json()
        
        # Send the data to the second API
        second_api_url = "http://127.0.0.1:5000/api/generate"  # Replace with your second API URL
        second_response = requests.post(second_api_url, json={
            "retrieved_content": response_data,  # Pass the list directly
            "query": user_input
        })
        second_response.raise_for_status()  # Raise an error for bad HTTP responses
        second_response_data = second_response.json()
        
        # Append the result from the second API to the chat_data
        bot_response = second_response_data.get('response', 'No response from second API')
        chat_data.append({
            "text": bot_response,
            "isBot": True
        })
        
    except requests.exceptions.RequestException as e:
        return Response({"status": f"External API request error: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)
    
    # Save chat data to cache
    cache.set('current_chat', chat_data)
    
    # Return the updated chat_data to api.js
    return Response({"status": "Chat saved to cache", "chat_data": chat_data}, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_cache_to_db(request):
    chat_data = cache.get('current_chat')
    chat_id = request.data.get('chat_id', None)
    
    if not chat_data:
        return Response({"status": "No chat found in cache"}, status=status.HTTP_400_BAD_REQUEST)
    
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
    return Response({"status": "Chat saved to DB", "chat_id": chat_id}, status=status.HTTP_200_OK)

@api_view(['GET'])
def fetch_chat_from_db(request, chat_id):
    try:
        chat = Chat.objects.get(id=chat_id)
        return Response(chat.input_response_pairs, status=status.HTTP_200_OK)
    except Chat.DoesNotExist:
        return Response({"error": "Chat not found"}, status=status.HTTP_404_NOT_FOUND)
