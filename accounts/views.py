from django.contrib.auth import authenticate, login, logout
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from .serializers import UserSerializer

class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        ser = UserSerializer(data=request.data)
        if ser.is_valid():
            u = ser.save()
            return Response(UserSerializer(u).data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        u = request.data.get('username')
        p = request.data.get('password')
        user = authenticate(username=u, password=p)
        if user:
            login(request, user)
            return Response(UserSerializer(user).data)
        return Response({'error':'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        logout(request)
        return Response({'message':'Successfully logged out'})

class UserDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        return Response(UserSerializer(request.user).data)
    def put(self, request):
        ser = UserSerializer(request.user, data=request.data, partial=True)
        if ser.is_valid():
            u = ser.save()
            return Response(UserSerializer(u).data)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_users_by_type(request, user_type):
    qs = User.objects.filter(profile__user_type=user_type.upper())
    return Response(UserSerializer(qs, many=True).data)
