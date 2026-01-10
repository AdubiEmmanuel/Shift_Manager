from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .forms import UserLoginForm

app_name = "users"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="users/login.html",
            authentication_form=UserLoginForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="users:login"), name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("create_user/", views.create_user_view, name="create_user"),
    path("create_user_ajax/", views.create_user_ajax, name="create_user_ajax"),
    path("users/", views.user_list_view, name="user_list"),
    path("users/<int:pk>/edit/", views.user_edit_view, name="user_edit"),
    path("users/<int:pk>/delete/", views.user_delete_view, name="user_delete"),
]
