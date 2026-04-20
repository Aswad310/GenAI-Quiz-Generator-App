from rest_framework import generics
from rest_framework.views import APIView, Response, status
from core.responses import BaseResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import UserSignUpAPIViewSerializer, UserLoginAPIViewSerializer, UserSerializer, \
    VerifyOtpAPIViewSerializer, ResendOtpAPIViewSerializer, GoogleLoginAPIViewSerializer, \
    ChangePasswordAPIViewSerializer, PasswordRestAPIViewSerializer, PasswordResetConfirmAPIViewSerializer
from django.db import transaction


class UserSignUpAPIView(APIView):
    @transaction.atomic()
    def post(self, requests):
        return BaseResponse({"tokens": tokens}, message=message, status_code=status_code)


class UserLoginAPIView(APIView):
    @transaction.atomic()
    def post(self, requests):
        user_login_serializer = UserLoginAPIViewSerializer(data=requests.data)
        user_login_serializer.is_valid(raise_exception=True)
        data = {
            "email_is_verified": user_login_serializer.validated_data.get("email_is_verified"),
            "tokens": user_login_serializer.validated_data.get("tokens")
        }
        return BaseResponse(
            data,
            message=user_login_serializer.validated_data.get("message"),
            status_code=user_login_serializer.validated_data.get("status_code")
        )


class UserAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]

    @transaction.atomic()
    def post(self, request):
        serializer = UserSerializer(request.user)
        return BaseResponse(serializer.data, message="User profile fetched successfully.")


class VerifyOtpAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]

    @transaction.atomic()
    def post(self, request):
        otp_serializer = VerifyOtpAPIViewSerializer(data=data)
        otp_serializer.is_valid(raise_exception=True)
        return BaseResponse(message=otp_serializer.validated_data.get("message"))


class ResendOtpAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]

    @transaction.atomic()
    def post(self, request):
        resend_otp_serializer = ResendOtpAPIViewSerializer(data=data)
        resend_otp_serializer.is_valid(raise_exception=True)
        return BaseResponse(
            message=resend_otp_serializer.validated_data.get("message"),
            status_code=resend_otp_serializer.validated_data.get("status_code")
        )


class GoogleLoginAPIView(APIView):
    @transaction.atomic()
    def post(self, request):
        google_response_serializer = GoogleLoginAPIViewSerializer(data=request.data)
        google_response_serializer.is_valid(raise_exception=True)
        data = {
            "email_is_verified": google_response_serializer.validated_data.get("email_is_verified", False),
            "tokens": google_response_serializer.validated_data.get("tokens", None)
        }
        return BaseResponse(
            data,
            message=google_response_serializer.validated_data.get("message", None),
            status_code=google_response_serializer.validated_data.get("status_code", status.HTTP_200_OK)
        )


class ChangePasswordAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]

    @transaction.atomic()
    def post(self, request):
        change_password_serializer = ChangePasswordAPIViewSerializer(request.user, data=request.data,
                                                                     context=user)
        change_password_serializer.is_valid(raise_exception=True)
        message, status_code = change_password_serializer.save()
        return BaseResponse(message=message, status_code=status_code)


class PasswordResetAPIView(APIView):

    def post(self, request):
        email_serializer = PasswordRestAPIViewSerializer(data=request.data)
        email_serializer.is_valid(raise_exception=True)
        return BaseResponse(
            message=email_serializer.validated_data.get("message", None),
            status_code=email_serializer.validated_data.get("status_code", status.HTTP_200_OK)
        )


class PasswordResetConfirmAPIView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmAPIViewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return BaseResponse(message="Password reset complete")
