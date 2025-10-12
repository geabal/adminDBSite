from django.urls import path
from . import views

app_name='contentAdmin'

urlpatterns = [
    path('', views.upload_index, name='upload_index'),
    path('upload/', views.upload_index, name='upload_index'),
    path('upload-csv/', views.upload_csv_api, name='upload_csv_api'),
    path('upload/upload-csv/', views.upload_csv_api, name='upload_csv_api'),
    path('download/', views.download_index, name='download_index'),
    path('download/create/', views.create_csv_file, name='create_csv_file'),
    path('download/file/<str:file_name>/', views.download_csv_file, name='download_csv_file')

]