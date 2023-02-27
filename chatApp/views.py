from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.
class MyAPIView(APIView):
    def get(self, request):
        # Retrieve data from the database or any other source
        data = {'key': 'value'}

        # Return the data in the response
        return Response(data)