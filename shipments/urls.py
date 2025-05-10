from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ShipmentViewSet, DeliveryPersonViewSet

router = DefaultRouter()
router.register(r'delivery-persons', DeliveryPersonViewSet, basename='delivery-person')
router.register(r'', ShipmentViewSet, basename='shipment')

urlpatterns = [
    path('', include(router.urls)),
]
