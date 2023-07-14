from django.urls import path
from user_management import views

urlpatterns = [
    path("manage-user/", views.Users.as_view()),
    path("manage-groups/", views.Groups.as_view())
]