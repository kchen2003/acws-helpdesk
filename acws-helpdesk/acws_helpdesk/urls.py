from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from helpdesk.forms import CustomAuthForm

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("helpdesk.urls", namespace="helpdesk")),
    path("accounts/login/", auth_views.LoginView.as_view(authentication_form=CustomAuthForm, template_name='registration/login.html'), name='login'),
    path("accounts/", include("django.contrib.auth.urls")),
]
