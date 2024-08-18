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


def assign_message_ids(chat_data: list) -> list:
    """
    Assign unique IDs to each message in chat_data.

    Args:
    chat_data (list): A list of dictionaries representing chat messages. Each dictionary should have a 'text' key and an optional 'id' key.
   
    Returns:
    list: The input chat_data with each message assigned a unique ID.
    """
    for message in chat_data:
        if 'id' not in message:
            message['id'] = str(uuid.uuid4())
    return chat_data


def process_mapping_query(user_input: str, option: str) -> tuple:
    """
    Process the mapping query by sending it to the external API.

    Args:
    user_input (str): The input query to be processed.
    option (str): The mode of processing, either 'mapping' or 'generation'.

    Returns:
    tuple: A tuple containing the response data from the external API and an optional error message.
    If the response data is not None, it is a dictionary containing the processed query.
    If there is an error during the API request, the second element of the tuple is a string containing the error message.
    """
    api_url = "http://127.0.0.1:5000/api/query"
    try:
        response = requests.post(api_url, json={"query": user_input, "mode": option})
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, f"External API request error: {str(e)}"


def find_best_matching_question(user_input, cached_questions, threshold=0.5):
    """
    Find the best matching question from the cached_questions.

    Args:
    user_input (str): The input query to be matched with cached questions.
    cached_questions (list): A list of dictionaries containing cached questions. Each dictionary should have a 'question' key and an optional 'data' key.
    threshold (float, optional): A similarity threshold to determine the best matching question. Defaults to 0.5.

    Returns:
    dict or None: The dictionary containing the best matching question's data if found, otherwise None.
    """
    user_input_vector = model.encode(user_input, convert_to_tensor=True)
    best_match_data = None
    best_match_score = 0

    for cached_question in cached_questions:
        cached_question_vector = model.encode(cached_question['question'], convert_to_tensor=True)
        similarity = util.pytorch_cos_sim(user_input_vector, cached_question_vector).item()
        if similarity > threshold and similarity > best_match_score:
            best_match_data = cached_question['data']
            best_match_score = similarity

    return best_match_data


def optimize_query(user_input: str) -> tuple:
    """
    Optimize the user query using an external API.

    Args:
    user_input (str): The input query to be optimized.

    Returns:
    tuple: A tuple containing the optimized query or the original query if no optimization is performed, and an optional error message.
    If the response data is not None, it is a string containing the optimized query.
    If there is an error during the API request, the second element of the tuple is a string containing the error message.
    """
    query_optimization_url = "http://127.0.0.1:5050/process_query"
    try:
        response = requests.post(query_optimization_url, json={"query": user_input})
        response.raise_for_status()
        return response.json().get('optimized_query', user_input), None
    except requests.exceptions.RequestException as e:
        return None, f"Query optimization API request error: {str(e)}"


def fetch_response_from_external_api(query, option):
    """
    Fetch the response from an external API based on the query and option.

    Args:
    query (str): The input query to be processed.
    option (str): The mode of processing, either 'mapping' or 'generation'.

    Returns:
    tuple: A tuple containing the response data from the external API and an optional error message.
    If the response data is not None, it is a dictionary containing the processed query.
    If there is an error during the API request, the second element of the tuple is a string containing the error message.
    """
    external_api_url = "http://127.0.0.1:5000/api/query"
    try:
        response = requests.post(external_api_url, json={"query": query, "mode": option})
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, f"External API request error: {str(e)}"


def handle_top_3_questions(top_3_questions, cached_questions):
    """
    Send each top 3 questions to an external API and save responses.

    Args:
    top_3_questions (list): A list of strings containing the top 3 questions to be sent to the external API.
    cached_questions (list): A list of dictionaries containing cached questions. Each dictionary should have a 'question' key and an optional 'data' key.

    Returns:
    None: This function does not return any value. It only sends the top 3 questions to the external API and saves the responses in the 'cached_questions' list.

    Raises:
    requests.exceptions.RequestException: If there is an error during the API request, this exception will be raised.

    Note:
    This function uses the 'requests' library to send HTTP requests to the external API. It also assumes that there is a 'question_cache' object that can be used to store the 'cached_questions' list.
    """
    external_api_url = "http://127.0.0.1:5000/api/query"
    for question in top_3_questions:
        if question:
            try:
                response = requests.post(external_api_url, json={"query": question, "mode": "generation"})
                response.raise_for_status()
                question_response_data = response.json()
                cached_questions.append({
                    'question': question,
                    'data': question_response_data
                })
            except requests.exceptions.RequestException:
                continue  # Ignore errors for individual question responses
    question_cache.set('cached_questions', cached_questions)


@api_view(['GET'])
def list_chats(request):
    """
    Retrieves a list of all chats in descending order of their creation timestamp.

    Args:
    request (Request): The HTTP request object. This object is used to retrieve the data passed in the request.

    Returns:
    Response: An HTTP response containing a JSON representation of the list of chats. The response status code is set to 200 (OK).
    """
    chats = Chat.objects.all().order_by('-created_at')
    serializer = ChatSerializer(chats, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_chat(request):
    """
    Saves a chat to the database.

    Args:
    request (Request): The HTTP request object. This object is used to retrieve the data passed in the request.

    Returns:
    Response: An HTTP response containing a JSON representation of the saved chat. The response status code is set to 201 (Created) if the chat is successfully saved, or 400 (Bad Request) if the chat data is invalid.
    """
    serializer = ChatSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def save_chat_to_cache(request):
    """
    Saves a chat to the cache and returns a response with the saved chat data, similar question, and status.
    
    Args:
    request (Request): The HTTP request object. This object is used to retrieve the data passed in the request.
    
    Returns:
    Response: An HTTP response containing a JSON representation of the saved chat data, similar question, and status. The response status code is set to 200 (OK) if the chat is successfully saved, or 400 (Bad Request) if the chat data is invalid.
    
    Raises:
    requests.exceptions.RequestException: If there is an error during the API request, this exception will be raised.
    
    Note:
    This function uses the 'requests' library to send HTTP requests to the external API. It also assumes that there is a 'question_cache' object that can be used to store the 'cached_questions' list.
    """
    chat_data = request.data.get('chat_data')
    option = request.data.get('option', 'Generation')

    if not chat_data:
        return Response({"status": "No chat data provided"}, status=status.HTTP_400_BAD_REQUEST)

    # Assign unique IDs to messages
    chat_data = assign_message_ids(chat_data)

    user_input = chat_data[-1].get('text')
    if option == 'mapping':
        response_data, error = process_mapping_query(user_input, option)
        if error:
            return Response({"status": error}, status=status.HTTP_502_BAD_GATEWAY)
        return Response({"status": "Chat saved to cache", "response_data": response_data}, status=status.HTTP_200_OK)

    try:
        # Retrieve cached questions from the cache
        cached_questions = question_cache.get('cached_questions', [])
        matched_question_data = find_best_matching_question(user_input, cached_questions)

        if matched_question_data:
            bot_response = matched_question_data.get('answer', 'No response from cached data')
            similar_question = matched_question_data.get('highest_similar_question', '')
        else:
            optimized_query, error = optimize_query(user_input)
            if error:
                return Response({"status": error}, status=status.HTTP_502_BAD_GATEWAY)

            response_data, error = fetch_response_from_external_api(optimized_query, option)
            if error:
                return Response({"status": error}, status=status.HTTP_502_BAD_GATEWAY)
            bot_response = response_data.get('answer', 'No response from second API')

            send_data_api_url = "http://127.0.0.1:5060/ask"
            try:
                send_data_response = requests.post(send_data_api_url, json={"chat_data": optimized_query})
                send_data_response.raise_for_status()
                api_response_data = send_data_response.json()
            except requests.exceptions.RequestException as e:
                return Response({"status": f"Send data API request error: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)

            handle_top_3_questions(api_response_data.get('top_3_questions', []), cached_questions)
            similar_question = api_response_data.get('highest_similar_question', '')

        question_cache.delete('current_chat')

        bot_message_id = str(uuid.uuid4())
        chat_data.append({
            "id": bot_message_id,
            "text": bot_response,
            "isBot": True
        })

    except Exception as e:
        return Response({"status": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    last_response = chat_data[-1]
    default_cache.set('current_chat', [last_response])

    return Response({"status": "Chat saved to cache", "chat_data": [last_response], "similar_question": similar_question}, status=status.HTTP_200_OK)

@api_view(['POST'])
def save_cache_to_db(request):
    """
    Saves the chat data from the cache to the database and returns a response with the saved chat ID.
    
    Args:
    request (Request): The HTTP request object. This object is used to retrieve the data passed in the request.
    chat_data (list): A list of dictionaries containing the chat data. Each dictionary should have 'text' and 'isBot' keys.
    chat_id (int, optional): The ID of the chat to be saved. If not provided, a new chat will be created.
    
    Returns:
    Response: An HTTP response containing a JSON representation of the saved chat ID. The response status code is set to 200 (OK) if the chat is successfully saved, or 400 (Bad Request) if the chat data is invalid.
    
    Raises:
    Chat.DoesNotExist: If the chat with the provided ID does not exist, this exception will be raised.
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
    Retrieves a chat from the database based on the provided chat ID.

    Args:
    request (Request): The HTTP request object. This object is used to retrieve the data passed in the request.

    chat_id (int): The unique identifier of the chat to be retrieved from the database.

    Returns:
    Response: An HTTP response containing a JSON representation of the chat's input and response pairs. The response status code is set to 200 (OK) if the chat is successfully retrieved, or 404 (Not Found) if the chat with the provided ID does not exist.
    """
    try:
        chat = Chat.objects.get(id=chat_id)
        return Response(chat.input_response_pairs, status=status.HTTP_200_OK)
    except Chat.DoesNotExist:
        return Response({"error": "Chat not found"}, status=status.HTTP_404_NOT_FOUND)
