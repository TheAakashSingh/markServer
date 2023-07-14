from rest_framework import serializers

class ForgotPassReqSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

class ResetPassReqSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)