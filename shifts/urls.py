from django.urls import path

from . import views

app_name = "shifts"

urlpatterns = [
    path("leaves/", views.leave_list_view, name="leave_list"),
    path("leaves/new/", views.leave_create_view, name="leave_create"),
    path("leaves/<int:pk>/approve/", views.approve_leave_view, name="leave_approve"),
]
