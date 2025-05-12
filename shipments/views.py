import tempfile
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from .models import Shipment, BananaImage, DeliveryPerson
from .serializers import ShipmentSerializer, DeliveryPersonSerializer
from .utils import get_optimized_route
from ml.utils import predict_banana_ripeness


class DeliveryPersonViewSet(viewsets.ModelViewSet):
    queryset = DeliveryPerson.objects.all().order_by('user__id')
    serializer_class = DeliveryPersonSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes     = [IsAuthenticated]


class ShipmentViewSet(viewsets.ModelViewSet):
    serializer_class = ShipmentSerializer
    
    def get_queryset(self):
        queryset = Shipment.objects.all()
        
        # Get query parameters
        status = self.request.query_params.get('status')
        delivery_person_id = self.request.query_params.get('delivery_person')
        
        # Filter by query parameters if provided
        if status:
            statuses = status.split(',')
            queryset = queryset.filter(status__in=statuses)
        
        # Check if the user is associated with a delivery person profile
        if not delivery_person_id:
            try:
                # Try to get delivery person profile for current user
                delivery_person = DeliveryPerson.objects.get(user=self.request.user)
                # Only show shipments assigned to this delivery person
                queryset = queryset.filter(delivery_person=delivery_person)
            except DeliveryPerson.DoesNotExist:
                # If not a delivery person, show based on other roles (like farmers see what they created)
                if hasattr(self.request.user, 'profile') and self.request.user.profile.user_type == 'FARMER':
                    queryset = queryset.filter(created_by=self.request.user)
                elif hasattr(self.request.user, 'profile') and self.request.user.profile.user_type == 'RETAILER':
                    queryset = queryset.filter(receiver=self.request.user)
        else:
            # Explicit delivery_person filter was provided
            queryset = queryset.filter(delivery_person_id=delivery_person_id)
            
        return queryset