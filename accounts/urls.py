from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView, UserDetailView, get_users_by_type
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/',    LoginView.as_view(),    name='login'),
    path('logout/',   LogoutView.as_view(),   name='logout'),
    path('user/',     UserDetailView.as_view(), name='user-detail'),
    path('users/<str:user_type>/', get_users_by_type, name='users-by-type'),
]
