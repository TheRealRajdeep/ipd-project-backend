import tempfile
from rest_framework import serializers
from django.conf import settings
from django.contrib.auth.models import User
from ml.utils import predict_banana_ripeness

from .models import Shipment, BananaImage, DeliveryPerson


class DateOnlyField(serializers.DateField):
    def to_representation(self, value):
        if hasattr(value, 'date'):
            value = value.date()
        return super().to_representation(value)


class UserBriefSerializer(serializers.ModelSerializer):
    user_type = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id','username','first_name','last_name','email','user_type']

    def get_user_type(self, obj):
        return getattr(getattr(obj,'profile',None),'user_type',None)


class DeliveryPersonSerializer(serializers.ModelSerializer):
    id      = serializers.CharField(read_only=True)
    user    = UserBriefSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = DeliveryPerson
        fields = ['id','user','user_id','phone_number','vehicle_info']

    def create(self, validated_data):
        user = User.objects.get(id=validated_data.pop('user_id'))
        return DeliveryPerson.objects.create(user=user, **validated_data)


class BananaImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BananaImage
        fields = ['id','uploaded_at']


class ShipmentSerializer(serializers.ModelSerializer):
    id                  = serializers.CharField(read_only=True)
    shipment_date       = DateOnlyField()
    estimated_arrival   = DateOnlyField(allow_null=True)
    created_by          = UserBriefSerializer(read_only=True)
    receiver            = UserBriefSerializer(read_only=True)
    delivery_person     = DeliveryPersonSerializer(read_only=True)

    created_by_id       = serializers.IntegerField(write_only=True)
    receiver_id         = serializers.IntegerField(write_only=True)
    delivery_person_id  = serializers.PrimaryKeyRelatedField(
                              source='delivery_person',
                              queryset=DeliveryPerson.objects.all(),
                              write_only=True, required=False, allow_null=True
                          )

    image               = serializers.ImageField(write_only=True, required=False)
    images              = BananaImageSerializer(many=True, read_only=True)
    ripeness_summary    = serializers.JSONField(read_only=True)
    optimized_route     = serializers.JSONField(read_only=True)
    map_url             = serializers.CharField(read_only=True)

    class Meta:
        model = Shipment
        fields = [
            'id',
            'created_by','created_by_id',
            'receiver','receiver_id',
            'delivery_person','delivery_person_id',
            'origin','destination','quantity','status',
            'shipment_date','estimated_arrival',
            'ripeness_status','dominant_ripeness','ripeness_summary',
            'shelf_life','result_image',
            'current_lat','current_lon','optimized_route','map_url',
            'created_at','last_updated','images','image',
        ]
        read_only_fields = ['id','created_at','last_updated','alert_sent']

    def _dump_to_temp(self, file_obj):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            for chunk in file_obj.chunks():
                tmp.write(chunk)
            tmp.flush()
            return tmp.name

    def _run_prediction(self, tmp_path):
        weights = getattr(settings,'WEIGHTS_PATH',None)
        mapping = getattr(settings,'MAPPING_PATH',None)
        return predict_banana_ripeness(tmp_path, weights, mapping)

    def create(self, validated_data):
        img = validated_data.pop('image', None)
        cb = User.objects.get(id=validated_data.pop('created_by_id'))
        rc = User.objects.get(id=validated_data.pop('receiver_id'))
        dp = validated_data.pop('delivery_person', None)

        shipment = Shipment.objects.create(
            created_by=cb, receiver=rc, **validated_data
        )

        if dp:
            shipment.delivery_person = dp
            shipment.status = 'IN_TRANSIT'
            shipment.save()

        if img:
            tmp_path = self._dump_to_temp(img)
            out, b64 = self._run_prediction(tmp_path)
            shipment.ripeness_summary   = out['ripeness']
            shipment.dominant_ripeness   = out['dominant_ripeness']
            shipment.shelf_life          = out['shelf_life']
            shipment.result_image        = b64
            shipment.save()
            BananaImage.objects.create(shipment=shipment, image_data=img.read())

        return shipment

    def update(self, instance, validated_data):
        img = validated_data.pop('image', None)
        dp  = validated_data.pop('delivery_person', None)
        instance = super().update(instance, validated_data)

        if dp is not None:
            instance.delivery_person = dp
            instance.status = 'IN_TRANSIT'
            instance.save()

        if img:
            tmp_path = self._dump_to_temp(img)
            out, b64 = self._run_prediction(tmp_path)
            instance.ripeness_summary   = out['ripeness']
            instance.dominant_ripeness   = out['dominant_ripeness']
            instance.shelf_life          = out['shelf_life']
            instance.result_image        = b64
            instance.save()
            BananaImage.objects.create(shipment=instance, image_data=img.read())

        return instance
