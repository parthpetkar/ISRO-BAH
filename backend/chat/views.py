from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ChatSerializer

@api_view(['POST'])
def save_chat(request):
    if request.method == 'POST':
        serializer = ChatSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
