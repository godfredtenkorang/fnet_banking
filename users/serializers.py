from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone_number', 'email']

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    
    def validate(self, attrs):
        phone_number =attrs.get('phone_number')
        password = attrs.get('password')
        
        user = authenticate(request=self.context.get('request'), phone_number=phone_number, password=password)
        
        if not user:
            raise serializers.ValidationError('Invalid phone or password')
        
        refresh = RefreshToken.for_user(user)
        
        return {
            'user': UserSerializer(user).data,
            'token': str(refresh.access_token),
        }