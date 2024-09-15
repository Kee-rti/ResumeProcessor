from django.urls import path
from .views import ExtractResumeView

urlpatterns = [
    path('extract_resume/', ExtractResumeView.as_view(), name='extract_resume'),
]