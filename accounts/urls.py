from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RegisterView, LoginView, LogoutView, UserViewSet, UserDetailView, get_users_by_type
)

router = DefaultRouter()
router.register('users', UserViewSet)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/',    LoginView.as_view(),    name='login'),
    path('logout/',   LogoutView.as_view(),   name='logout'),
    path('user/',     UserDetailView.as_view(), name='user-detail'),
    path('users/<str:user_type>/', get_users_by_type, name='users-by-type'),
]
