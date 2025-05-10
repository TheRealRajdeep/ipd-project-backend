from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user_type', 'phone_number', 'address', 'company_name']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()
    class Meta:
        model = User
        fields = ['id','username','email','first_name','last_name','password','profile']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        prof = validated_data.pop('profile')
        pwd = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if pwd:
            user.set_password(pwd)
            user.save()
        UserProfile.objects.create(user=user, **prof)
        return user

    def update(self, instance, validated_data):
        prof = validated_data.pop('profile', None)
        pwd = validated_data.pop('password', None)
        if pwd:
            instance.set_password(pwd)
        for k,v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        if prof:
            p = instance.profile
            for k,v in prof.items():
                setattr(p, k, v)
            p.save()
        return instance
