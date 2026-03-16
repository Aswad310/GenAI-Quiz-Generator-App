from rest_framework import generics
from rest_framework.views import APIView, Response, status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import UserSignUpAPIViewSerializer, UserLoginAPIViewSerializer, UserSerializer, \
    VerifyOtpAPIViewSerializer, ResendOtpAPIViewSerializer, GoogleLoginAPIViewSerializer, \
    ChangePasswordAPIViewSerializer, PasswordRestAPIViewSerializer, PasswordResetConfirmAPIViewSerializer
from django.db import transaction


class UserSignUpAPIView(APIView):
    @transaction.atomic()
    def post(self, requests):
        response = dict()
        user_signup_serializer = UserSignUpAPIViewSerializer(data=requests.data)
        user_signup_serializer.is_valid(raise_exception=True)
        tokens, message, status_code = user_signup_serializer.save()
        response["status_code"] = status_code
        response["message"] = message
        response["tokens"] = tokens
        return Response(response, status=status_code)


class UserLoginAPIView(APIView):
    @transaction.atomic()
    def post(self, requests):
        response = dict()
        user_login_serializer = UserLoginAPIViewSerializer(data=requests.data)
        user_login_serializer.is_valid(raise_exception=True)
        response["status_code"] = user_login_serializer.validated_data.get("status_code")
        response["message"] = user_login_serializer.validated_data.get("message")
        response["email_is_verified"] = user_login_serializer.validated_data.get("email_is_verified")
        response["tokens"] = user_login_serializer.validated_data.get("tokens")
        return Response(response, status=response["status_code"])


class UserAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]

    @transaction.atomic()
    def post(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class VerifyOtpAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]

    @transaction.atomic()
    def post(self, request):
        response = dict()
        data = {
            "otp_code": request.data.get("otp_code"),
            "user": request.user.id
        }
        otp_serializer = VerifyOtpAPIViewSerializer(data=data)
        otp_serializer.is_valid(raise_exception=True)
        response["status_code"] = status.HTTP_200_OK
        response["message"] = otp_serializer.validated_data.get("message")
        return Response(response, status=status.HTTP_200_OK)


class ResendOtpAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]

    @transaction.atomic()
    def post(self, request):
        response = dict()
        data = {
            "user": request.user.id
        }
        resend_otp_serializer = ResendOtpAPIViewSerializer(data=data)
        resend_otp_serializer.is_valid(raise_exception=True)
        response["status_code"] = resend_otp_serializer.validated_data.get("status_code")
        response["message"] = resend_otp_serializer.validated_data.get("message")
        return Response(response, status=response["status_code"])


class GoogleLoginAPIView(APIView):
    @transaction.atomic()
    def post(self, request):
        response = dict()
        google_response_serializer = GoogleLoginAPIViewSerializer(data=request.data)
        google_response_serializer.is_valid(raise_exception=True)
        response["status_code"] = google_response_serializer.validated_data.get("status_code", None)
        response["message"] = google_response_serializer.validated_data.get("message", None)
        response["email_is_verified"] = google_response_serializer.validated_data.get("email_is_verified", False)
        response["tokens"] = google_response_serializer.validated_data.get("tokens", None)
        return Response(response, status=response["status_code"])


class ChangePasswordAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]

    @transaction.atomic()
    def post(self, request):
        response = dict()
        user = {'user': request.user}
        change_password_serializer = ChangePasswordAPIViewSerializer(request.user, data=request.data,
                                                                     context=user)
        change_password_serializer.is_valid(raise_exception=True)
        message, status_code = change_password_serializer.save()
        response["status_code"] = status_code
        response["message"] = message
        return Response(response, status=status_code)


class PasswordResetAPIView(APIView):

    def post(self, request):
        response = dict()
        email_serializer = PasswordRestAPIViewSerializer(data=request.data)
        email_serializer.is_valid(raise_exception=True)
        response["status_code"] = email_serializer.validated_data.get("status_code", None)
        response["message"] = email_serializer.validated_data.get("message", None)
        return Response(response, status=response["status_code"])


class PasswordResetConfirmAPIView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmAPIViewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"message": "Password reset complete"},
            status=status.HTTP_200_OK,
        )
