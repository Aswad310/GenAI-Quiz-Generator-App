from datetime import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import CustomUser, ManageOtp
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import transaction
from rest_framework import serializers, status
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken
from .helpers import generate_otp_and_send_email, check_google_auth_token, track_email, send_password_reset_email
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email')


class UserSignUpAPIViewSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(
        max_length=100,
        validators=[MinLengthValidator(8), MaxLengthValidator(20)]
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")
        if password != confirm_password:
            raise serializers.ValidationError(
                {'message': 'password and confirm password does not matched'}
            )
        return attrs

    @transaction.atomic()
    def create(self, validated_data):
        user_obj = CustomUser.objects.create_user(
            email=validated_data.get("email"),
            password=validated_data.get("password"),
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            is_google_login=validated_data.get("is_google_login", False),
        )
        res = generate_otp_and_send_email(user=user_obj, module_name='user_signup')
        if res == 1:
            refresh = RefreshToken.for_user(user_obj)
            message = "Successfully Signup and OTP sent to the given email for email verification." \
                      "And Please use the given access token to use others APIs. Thanks"
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return tokens, message, status.HTTP_200_OK
        elif res == 0:
            message = "Something went wrong. Please contact you admin. Thanks"
            token = dict()
            return token, message, status.HTTP_404_NOT_FOUND


class UserLoginAPIViewSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = attrs.get('user', None)
        password = attrs.get('password', None)
        print('user=====================>>', user)
        if user is None:
            user = CustomUser.objects.filter(email=attrs.get('email')).first()
            print(user)
        if user:
            if not attrs.get('google_login', None):
                if user.is_google_login and user.password == "":
                    raise serializers.ValidationError({'message': 'Your account is registered from google. Please login'
                                                                  'with google'})
            if password is not None:
                password_is_valid = user.check_password(password)
            else:
                password_is_valid = True
            if password_is_valid:
                refresh = RefreshToken.for_user(user)
                if user.email_is_verified:
                    attrs["status_code"] = status.HTTP_200_OK
                    attrs["message"] = "Successfully login! Please use the given access token to use others APIs."
                    attrs["email_is_verified"] = True
                    attrs["tokens"] = {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                    return attrs
                else:
                    res = generate_otp_and_send_email(user=user, module_name='user_login')
                    if res == 1:
                        attrs["status_code"] = status.HTTP_200_OK
                        attrs["message"] = "Successfully Login and OTP sent to the given email for email verification." \
                                           "And Please use the given access token to use others APIs. Thanks"
                        attrs["email_is_verified"] = False
                        attrs["tokens"] = {
                            'refresh': str(refresh),
                            'access': str(refresh.access_token),
                        }
                        return attrs
                    elif res == 0:
                        attrs["status_code"] = status.HTTP_404_NOT_FOUND
                        attrs["message"] = "Something went wrong. Please contact your admin. Thanks"
                        attrs["email_is_verified"] = None
                        attrs["tokens"] = dict()
                        return attrs
            else:
                raise serializers.ValidationError(
                    {'message': 'Wrong Password'}
                )
        else:
            raise serializers.ValidationError(
                {'message': 'Email address not found'}
            )


class VerifyOtpAPIViewSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all()
    )

    class Meta:
        model = ManageOtp
        fields = ["otp_code", 'user']

    def validate(self, attrs):
        user = attrs.get("user")
        otp = attrs.get("otp_code")

        otp_obj = ManageOtp.objects.filter(Q(user_id=user) & Q(status=1)).first()
        if otp_obj:
            expiry_datetime = timezone.make_naive(otp_obj.expiry)
            if otp_obj.otp_code == otp and datetime.now() < expiry_datetime:
                otp_obj.delete()
                user.email_is_verified = True
                user.save()
                attrs["message"] = "Email verification is completed"
                return attrs
            else:
                raise serializers.ValidationError({"message": "OTP is invalid or expired!"})
        else:
            raise serializers.ValidationError({"message": "No OTP found against this user"})


class ResendOtpAPIViewSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all()
    )

    def validate(self, attrs):
        user = attrs.get("user")
        is_able_to_resend_email = track_email(user=user, module_name='resend_otp', seconds=120)
        if is_able_to_resend_email is False:
            raise serializers.ValidationError({'message': 'Please retry after some minutes'})
        if user.email_is_verified:
            attrs["status_code"] = status.HTTP_208_ALREADY_REPORTED
            attrs["message"] = "Your email is already verified"
            return attrs
        res = generate_otp_and_send_email(user=user, module_name='resend_otp')
        if res == 1:
            attrs["status_code"] = status.HTTP_200_OK
            attrs["message"] = "OTP Resent to your email"
            return attrs
        elif res == 0:
            attrs["status_code"] = status.HTTP_404_NOT_FOUND
            attrs["message"] = "Something went wrong. Please contact your admin. Thanks"
            return attrs


class GoogleLoginAPIViewSerializer(UserLoginAPIViewSerializer):
    authToken = serializers.CharField()
    password = serializers.CharField(required=False)
    id = serializers.IntegerField()
    name = serializers.CharField()
    photoUrl = serializers.CharField()
    provider = serializers.CharField()

    def validate(self, attrs):
        signup_serializer_obj = UserSignUpAPIViewSerializer()
        google_token = attrs.get('authToken')
        email = attrs.get('email')
        google_id = attrs.get('id')
        name = attrs.get('name')
        google_token_is_valid = check_google_auth_token(google_token)
        if google_token_is_valid:
            user_obj = CustomUser.objects.filter(email=email).first()
            attrs['user'] = user_obj
            if user_obj:
                attrs['google_login'] = True
                super().validate(attrs)
                return attrs
            else:
                split_name = name.rsplit(' ', 1) if ' ' in name else name
                validated_data = {
                    'email': email,
                    'first_name': split_name[0] if len(split_name) >= 1 else '',
                    'last_name': split_name[1] if len(split_name) >= 2 else '',
                    'is_google_login': True
                }
                tokens, message, status = signup_serializer_obj.create(validated_data)
                attrs['tokens'] = tokens
                attrs['message'] = message
                attrs['status_code'] = status
                return attrs
        else:
            raise serializers.ValidationError({'message': 'Token is invalid or expired!'})


class ChangePasswordAPIViewSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(
        max_length=100,
        required=True,
        validators=[MinLengthValidator(8), MaxLengthValidator(20)]
    )

    class Meta:
        model = CustomUser
        fields = ['old_password', 'password', 'confirm_password']

    def validate(self, attrs):
        user = self.context['user']
        old_password = attrs.get('old_password')
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")
        # Check old password if it matches
        if not user.check_password(old_password):
            raise serializers.ValidationError(
                {"message": "Old password doesn't match your existing password"},
            )
        # Check if password and confirm password is equal
        if password != confirm_password:
            raise serializers.ValidationError(
                {'message': 'Password and confirm password does not match.'}
            )
        # Check if old password is similar to new password
        if old_password == password:
            raise serializers.ValidationError(
                {"message": "Your new password is similar to the existing password."
                            " Please set different password."},
            )
        return attrs

    @transaction.atomic()
    def update(self, instance, validated_data):
        # Update new password
        instance.set_password(validated_data.get('password'))
        instance.save()
        message = "Password updated successfully."
        return message, status.HTTP_200_OK


class PasswordRestAPIViewSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get("email")
        user = CustomUser.objects.filter(email=email).first()
        if user:
            encoded_pk = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            reset_link = f"https://closedwon.us/reset_password?id={encoded_pk}-{token}"
            res = send_password_reset_email(user, reset_link, "reset_password")
            if res == 1:
                attrs["status_code"] = status.HTTP_200_OK
                attrs["message"] = "Forget password link send to your email"
                return attrs
            elif res == 0:
                attrs["status_code"] = status.HTTP_404_NOT_FOUND
                attrs["message"] = "Something went wrong. Please contact your admin. Thanks"
                return attrs
        else:
            attrs["status_code"] = status.HTTP_404_NOT_FOUND
            attrs["message"] = "User doesn't exists"
            return attrs


class PasswordResetConfirmAPIViewSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(
        max_length=100,
        required=True,
        validators=[MinLengthValidator(8), MaxLengthValidator(20)]
    )
    token = serializers.CharField(max_length=100)

    # encoded_pk = serializers.CharField(max_length=255)
    class Meta:
        model = CustomUser
        fields = ['password', 'confirm_password', 'token']

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")
        token = attrs.get("token")
        encoded_pk, token = token.split("-", maxsplit=1)
        print(encoded_pk)
        print(token)
        if token is None or encoded_pk is None:
            raise serializers.ValidationError({"message": "Missing data."})

        if password != confirm_password:
            raise serializers.ValidationError(
                {'message': 'Password and confirm password does not match.'}
            )
        try:
            pk = urlsafe_base64_decode(encoded_pk).decode()
        except:
            raise serializers.ValidationError(
                {'message': 'The reset token is invalid'}
            )
        user = CustomUser.objects.get(pk=pk)
        if not PasswordResetTokenGenerator().check_token(user, token) or not user:
            raise serializers.ValidationError({'message': 'The reset token is invalid'})
        user.set_password(password)
        user.save()

        return attrs
