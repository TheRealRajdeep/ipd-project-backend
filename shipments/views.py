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
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes     = [IsAuthenticated]

    @action(detail=True, methods=["post"], parser_classes=[MultiPartParser, FormParser], permission_classes=[AllowAny])
    def upload_image(self, request, pk=None):
        shipment = self.get_object()
        img = request.FILES.get('image')
        if not img:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            for chunk in img.chunks():
                tmp.write(chunk)
            tmp.flush()
            path = tmp.name

        out, b64 = predict_banana_ripeness(path, settings.WEIGHTS_PATH, settings.MAPPING_PATH)
        shipment.ripeness_summary   = out['ripeness']
        shipment.predictions        = out['predictions']
        shipment.dominant_ripeness  = out['dominant_ripeness']
        shipment.shelf_life         = out['shelf_life']
        shipment.result_image       = b64
        shipment.save()

        BananaImage.objects.create(shipment=shipment, image_data=img.read())
        return Response(out)

    @action(detail=True, methods=["post"], url_path='update_location')
    def update_location(self, request, pk=None):
        shipment = self.get_object()
        lat = request.data.get('latitude')
        lon = request.data.get('longitude')
        if lat is None or lon is None:
            return Response({'error':'latitude and longitude required'}, status=status.HTTP_400_BAD_REQUEST)

        shipment.current_lat = float(lat)
        shipment.current_lon = float(lon)
        if request.data.get('optimized_route'):
            shipment.optimized_route = request.data['optimized_route']
            shipment.save()
            return Response(self.get_serializer(shipment).data)
        return self.compute_route(request, pk)

    @action(detail=True, methods=["post"], url_path='compute_route')
    def compute_route(self, request, pk=None):
        shipment = self.get_object()
        route = get_optimized_route(shipment.origin, shipment.destination)
        shipment.optimized_route = route
        shipment.save()
        return Response({'optimized_route': route})

    @action(detail=True, methods=["post"], url_path='update_status')
    def update_status(self, request, pk=None):
        shipment = self.get_object()
        new = request.data.get('status')
        if new not in dict(Shipment.STATUS_CHOICES):
            return Response({'error':f'status must be one of {list(dict(Shipment.STATUS_CHOICES))}'}, status=status.HTTP_400_BAD_REQUEST)
        shipment.status = new
        shipment.save()
        return Response(self.get_serializer(shipment).data)

    @action(detail=True, methods=["post"], url_path='assign_delivery')
    def assign_delivery(self, request, pk=None):
        shipment = self.get_object()
        dp_id = request.data.get('delivery_person_id')
        if not dp_id:
            return Response({'error':'delivery_person_id required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            person = DeliveryPerson.objects.get(pk=dp_id)
        except DeliveryPerson.DoesNotExist:
            return Response({'error':'Invalid delivery_person_id'}, status=status.HTTP_400_BAD_REQUEST)

        shipment.delivery_person = person
        shipment.status = 'IN_TRANSIT'
        shipment.save()
        return Response(self.get_serializer(shipment).data)

    @action(detail=True, methods=["post"], url_path='mark_delivered')
    def mark_delivered(self, request, pk=None):
        shipment = self.get_object()
        shipment.status = 'DELIVERED'
        shipment.save()
        return Response(self.get_serializer(shipment).data)
