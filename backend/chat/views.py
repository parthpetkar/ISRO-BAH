import uuid
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import caches
from .models import Chat
from .serializers import ChatSerializer
from sentence_transformers import SentenceTransformer, util

# Use the default cache
default_cache = caches['default']
question_cache = caches['question']

# Initialize SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

@api_view(['GET'])
def list_chats(request):
    """
    Retrieve and return a list of all chats in the database, sorted by creation date in descending order.

    Parameters:
    request (Request): The incoming request object containing any query parameters or data.

    Returns:
    Response: A response object containing the serialized data of all chats. The HTTP status code is set to 200 OK.
    """
    chats = Chat.objects.all().order_by('-created_at')
    serializer = ChatSerializer(chats, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def save_chat(request):
    """
    Save a chat message to the database.

    Parameters:
    request (Request): The incoming request object containing the chat message data.

    Returns:
    Response: A response object containing the serialized data of the saved chat message. The HTTP status code is set to 201 CREATED if the chat message is successfully saved, or 400 BAD REQUEST if the chat message data is invalid.
    """
    serializer = ChatSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def save_chat_to_cache(request):
    """
    Save chat message to cache.

    This function takes a JSON object containing the chat data and an optional parameter 'option' which defaults to 'Generation'.
    The function processes the chat data, saves it to cache, and returns a response with the chat data and a similar question if available.

    Parameters:
    - chat_data (dict): A JSON object containing the chat data.
    - option (str, optional): An optional parameter specifying the mode for processing the chat data. Defaults to 'Generation'.

    Returns:
    - Response: A Django REST Framework response object containing the chat data and a similar question if available.
    """
    chat_data = request.data.get('chat_data')
    option = request.data.get('option', 'Generation')

    if not chat_data:
        return Response({"status": "No chat data provided"}, status=status.HTTP_400_BAD_REQUEST)

    # Assign unique IDs to messages
    for message in chat_data:
        message['id'] = str(uuid.uuid4())

    user_input = chat_data[-1].get('text')
    if option == 'mapping':
        api_url = "http://127.0.0.1:5000/api/query"
        try:
            response = requests.post(api_url, json={"query": user_input, "mode": option})
            response.raise_for_status()
            response_data = response.json()
            return Response({"status": "Chat saved to cache", "response_data": response_data}, status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as e:
            return Response({"status": f"External API request error: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)

    try:
        # Retrieve cached questions from the cache
        cached_questions = question_cache.get('cached_questions', [])
        matched_question_data = None
        
        # Convert user input to vector
        user_input_vector = model.encode(user_input, convert_to_tensor=True)
        threshold = 0.5
        best_match_score = 0
        
        # Check if the user_input matches any question in the cached_questions list
        for cached_question in cached_questions:
            cached_question_vector = model.encode(cached_question['question'], convert_to_tensor=True)
            similarity = util.pytorch_cos_sim(user_input_vector, cached_question_vector).item()
            if similarity > threshold and similarity > best_match_score:
                matched_question_data = cached_question['data']
                best_match_score = similarity

        if matched_question_data:
            # Retrieve response from the cache
            print(matched_question_data)
            bot_response = matched_question_data.get('answer', 'No response from cached data')
            similar_question = matched_question_data.get('highest_similar_question', '')
        else:
            # Process query and get response from external APIs
            query_optimization_url = "http://127.0.0.1:5050/process_query"
            try:
                response = requests.post(query_optimization_url, json={"query": user_input})
                response.raise_for_status()
                query_response_data = response.json()
                optimized_query = query_response_data.get('optimized_query', user_input)
            except requests.exceptions.RequestException as e:
                return Response({"status": f"Query optimization API request error: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)

            external_api_url = "http://127.0.0.1:5000/api/query"
            try:
                response = requests.post(external_api_url, json={"query": optimized_query, "mode": option})
                response.raise_for_status()
                response_data = response.json()
                bot_response = response_data.get('answer', 'No response from second API')
            except requests.exceptions.RequestException as e:
                return Response({"status": f"External API request error: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)

            send_data_api_url = "http://127.0.0.1:5060/ask"
            try:
                send_data_response = requests.post(send_data_api_url, json={"chat_data": optimized_query})
                send_data_response.raise_for_status()
                api_response_data = send_data_response.json()
            except requests.exceptions.RequestException as e:
                return Response({"status": f"Send data API request error: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)

            # Send each question in top_3_questions to external_api_url and save responses
            top_3_questions = api_response_data.get('top_3_questions', [])
            for question in top_3_questions:
                if question:
                    try:
                        response = requests.post(external_api_url, json={"query": question, "mode": "generation"})
                        response.raise_for_status()
                        question_response_data = response.json()
                        # Save each question and its response
                        cached_questions.append({
                            'question': question,
                            'data': question_response_data
                        })
                    except requests.exceptions.RequestException as e:
                        return Response({"status": f"Question API request error: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)

            # Cache the new response with all questions and their responses
            question_cache.set('cached_questions', cached_questions)

            similar_question = api_response_data.get('highest_similar_question', '')

        # Handle question cache
        question_cache.delete('current_chat')

        # Append bot response to chat_data
        bot_message_id = str(uuid.uuid4())
        chat_data.append({
            "id": bot_message_id,
            "text": bot_response,
            "isBot": True
        })

    except Exception as e:
        return Response({"status": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Save the last response to cache
    last_response = chat_data[-1]  # Assuming the last response is the bot's message
    default_cache.set('current_chat', [last_response])

    return Response({"status": "Chat saved to cache", "chat_data": [last_response], "similar_question": similar_question}, status=status.HTTP_200_OK)

@api_view(['POST'])
def save_cache_to_db(request):
    """
    Save the chat data from cache to the database.

    Parameters:
    - request (Request): The incoming request object containing the chat data and an optional parameter 'chat_id'.
    - chat_data (dict): A JSON object containing the chat data.
    - chat_id (int, optional): An optional parameter specifying the ID of the chat to be saved. Defaults to None.

    Returns:
    - Response: A Django REST Framework response object containing the chat data and a status message.
    """
    chat_data = default_cache.get('current_chat')
    chat_id = request.data.get('chat_id')

    if not chat_data:
        return Response({"status": "No chat found in cache"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        if chat_id:
            chat = Chat.objects.get(id=chat_id)
            chat.input_response_pairs = [chat_data[-1]]  # Only save the latest response
            chat.save()
        else:
            chat = Chat.objects.create(input_response_pairs=[chat_data[-1]])
            chat_id = chat.id

        default_cache.delete('current_chat')
        return Response({"status": "Chat saved to DB", "chat_id": chat_id}, status=status.HTTP_200_OK)
    except Chat.DoesNotExist:
        return Response({"error": "Chat not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def fetch_chat_from_db(request, chat_id: int) -> Response:
    """
    Retrieve a chat message from the database by its ID.

    Parameters:
    - request (Request): The incoming request object containing the chat ID.
    - chat_id (int): The unique identifier of the chat message to be retrieved.

    Returns:
    - Response: A Django REST Framework response object containing the chat message data. If the chat message is not found, the response will contain an error message with status code 404 NOT FOUND.
    """
    try:
        chat = Chat.objects.get(id=chat_id)
        return Response(chat.input_response_pairs, status=status.HTTP_200_OK)
    except Chat.DoesNotExist:
        return Response({"error": "Chat not found"}, status=status.HTTP_404_NOT_FOUND)

