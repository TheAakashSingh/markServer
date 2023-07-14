from rest_framework import serializers


class UserCreateReqSerializers(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=255)
    role = serializers.IntegerField()
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    date_of_birth = serializers.DateField()
    phone_no = serializers.IntegerField()
    gender = serializers.CharField(max_length=255)
    employee_id = serializers.CharField(max_length=255)
