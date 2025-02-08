from django.urls import path
from .views import user_register, user_login, resume_create, resume_preview, resume_download, home, token_refresh

urlpatterns = [
    path('', home, name='home'),  
    path('register/', user_register, name='register'),
    path('login/', user_login, name='login'),
    path('create/', resume_create, name='create_resume'),
    path('preview/', resume_preview, name='resume_preview'),
    path('download/', resume_download, name='resume_download'),
    path('token/refresh/', token_refresh, name='token_refresh'),
]
