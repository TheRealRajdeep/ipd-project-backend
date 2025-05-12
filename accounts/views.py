from django.contrib.auth import authenticate, login, logout
from rest_framework import viewsets, filters, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .serializers import UserSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'first_name', 'last_name', 'email']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        role = self.request.query_params.get('role', None)
        
        if role:
            # Filter users by their role in profile
            if role == 'retailer':
                queryset = queryset.filter(profile__role='retailer')
            elif role == 'farmer':
                queryset = queryset.filter(profile__role='farmer')
            elif role == 'distributor':
                queryset = queryset.filter(profile__role='distributor')
                
        return queryset
    
    @action(detail=False)
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        ser = UserSerializer(data=request.data)
        if ser.is_valid():
            u = ser.save()
            return Response(UserSerializer(u).data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

# Modify your LoginView class:
class LoginView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        u = request.data.get('username')
        p = request.data.get('password')
        user = authenticate(username=u, password=p)
        if user:
            login(request, user)
            # Generate token for the user
            from rest_framework.authtoken.models import Token
            token, created = Token.objects.get_or_create(user=user)
            # Get the user data
            serializer = UserSerializer(user)
            user_data = serializer.data
            # Include token in response
            user_data['auth_token'] = token.key
            return Response(user_data)
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
