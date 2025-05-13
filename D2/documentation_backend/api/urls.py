from django.urls import path
from .views import UploadRepoUrlView

urlpatterns = [
    path('upload-repo-url/', UploadRepoUrlView.as_view(), name='upload-repo-url'),
]

