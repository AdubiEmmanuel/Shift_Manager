from django.contrib import admin
from django.urls import include, path
from users import views as user_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls", namespace="users")),
    path("", user_views.home, name="home"),
    path("app/", include("shifts.urls", namespace="shifts")),
]
