from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('user-signup/', views.UserSignUpAPIView.as_view(), name='user_signup'),
    path('user-login/', views.UserLoginAPIView.as_view(), name='user_login'),
    path('user-detail/', views.UserAPIView.as_view(), name='user_detail'),
    path('verify-otp/', views.VerifyOtpAPIView.as_view(), name='verify_otp'),
    path('resend-otp/', views.ResendOtpAPIView.as_view(), name='verify_otp'),
    path('google-login/', views.GoogleLoginAPIView.as_view(), name='google_login'),
    path("password-reset/", views.PasswordResetAPIView.as_view(), name="password_reset"),
    path("password-reset-confirm/",
         views.PasswordResetConfirmAPIView.as_view(), name="password_reset_confirm"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
