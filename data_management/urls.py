from data_management import views
from django.urls import path

urlpatterns = [
    path("edit-data", views.EditData.as_view()),
    path('upload-data', views.UploadData.as_view()),
    path('view-data/', views.ViewCustomerData.as_view())
]