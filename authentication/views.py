import json

from django.shortcuts import render
import base64
import jwt
import logging
import re
import time
from datetime import datetime
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from authentication.models import UserLoginHistory
from authentication.serializers import ForgotPassReqSerializer, ResetPassReqSerializer
from user_management import permissions
from user_management.models import UserProfile
from utilities.date_time_utilities import current_epoch, epoch_to_date

logger = logging.getLogger(__name__)


class ForgotPassword(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPassReqSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = get_random_string(
            length=16,
            allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        )
        email = request.data.get("email")
        encoded_token = (
                email + "##" + str(current_epoch()) + "##" + token
        ).encode("utf-8")

        if not encoded_token:
            Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        user_detail = UserProfile.objects.filter(email - email).update(
            pass_token=token, token_time=epoch_to_date(int(time.time()))
        )
        if user_detail != 0:
            content = {"message": "Password recovery steps sent to registered mail"}
            return Response(content, status=status.HTTP_200_OK)
        else:
            content = {"message": "User details not found"}
            return Response(content, status=status.HTTP_404_NOT_FOUND)


class ResetPassword(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPassReqSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_token = request.data.get("token")
        user_password = request.data.get("password")
        invalid_token = False
        try:
            user_detail = (
                base64.urlsafe_b64decode(user_token).decode("utf-8").split("##")
            )
        except Exception as e:
            user_detail = []
            invalid_token = True
            logger.exception("Invalid token to reset password: {}".format(e))

        regex = r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w(2,3)$"
        content = {"message": "Password reset successful"}
        if not invalid_token and re.search(regex, user_detail[0]):
            try:
                user = UserProfile.objects.get(email=user_detail[0])
                if user.pass_token == user_detail[2]:
                    user.set_password(user_password)
                    user.pass_token = None
                    user.token_time = None
                    user.save()
                else:
                    invalid_token = True
            except UserProfile.DoesNotExist:
                invalid_token = True
        else:
            invalid_token = True
        if invalid_token:
            return Response(
                {"message": "Invalid Token"}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return Response(content, status=status.HTTP_200_OK)


class TokenObtainSerializer(TokenObtainPairSerializer):
    def get_token(cls, user):
        token = super().get_token(user)
        activity = [{'Activity': 'Logged In', 'Status': 'Successful', 'time': str(datetime.now())}]
        login_history = UserLoginHistory(user=user, IP="to get", activity=json.dumps(activity))
        login_history.save()

        token["first_name"] = user.first_name
        token["last_name"] = user.last_name
        token["employee_id"] = user.employee_id
        token["role"] = str(user.role)
        token["loginId"] = int(login_history.id)

        return token


class TokenView(TokenObtainPairView):
    serializer_class = TokenObtainSerializer


class Logout(APIView):
    permission_classes = [AllowAny ]

    def post(self, request):
        token = request.data.get("refresh-token")
        login_id_token = request.headers["Authorization"].split("Bearer ")[1]
        login_id = jwt.decode(login_id_token, options={"verify_signature": False})["loginId"]

        refresh_token = RefreshToken(token)
        refresh_token.blacklist()

        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")

        user_history = UserLoginHistory.objects.get(id=login_id)
        user_history.logouttime = datetime.now()
        user_history.IP = ip
        user_activity = json.loads(user_history.activity)
        user_activity.append({'Activity': 'Logged out', 'status': 'Successful', 'time': str(datetime.now())})
        user_activity = json.dumps(user_activity)
        user_history.activity = user_activity
        user_history.save()
        content = {"message": "Logged out"}
        return Response(content, status=status.HTTP_200_OK)


class LogData(APIView):
    permission_classes = [permissions.IsAdmin]

    @staticmethod
    def extract_user_activity(obj):
        if obj.activity:
            activity = json.loads(obj.activity)

            return activity

    def get(self, request):
        employee_id = request.GET.get('employee_id', None)
        log_data_dict = {}
        status_code = status.HTTP_200_OK
        if not employee_id:
            log_data = UserLoginHistory.objects.all().order_by('user__employee_id')
        else:
            log_data = UserLoginHistory.objects.filter(user__employee_id=employee_id).order_by('user__employee_id')
            if not log_data:
                status_code = status.HTTP_404_NOT_FOUND

        for data in log_data:
            activity = self.extract_user_activity(data)

            if activity:
                if log_data_dict.get(data.user.employee_id):
                    if isinstance(activity, list):
                        log_data_dict[data.user.employee_id].extend(activity)
                    else:
                        log_data_dict[data.user.employee_id].append(activity)
                else:
                    if isinstance(activity, dict):
                        log_data_dict[data.user.employee_id] = [activity]
                    else:
                        log_data_dict[data.user.employee_id] = activity
        return Response({'data': log_data_dict}, status_code)
