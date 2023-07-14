from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from authentication import views

urlpatterns = [
    path("login", views.TokenView.as_view(), name="token_obtain_pair"),
    path("refresh-access-token", jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
    path("forgot-password", views.ForgotPassword.as_view()),
    path("reset-password", views.ResetPassword.as_view()),
    path("logout", views.Logout.as_view()),
    path("user-activity/", views.LogData.as_view())
]