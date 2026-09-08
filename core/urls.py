from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("services/", views.browse_services, name="browse_services"),
    path("services/<int:pk>/", views.service_detail, name="service_detail"),
    path("services/<int:pk>/book/", views.book_service, name="book_service"),
    path("services/new/", views.add_service, name="add_service"),
    path("services/<int:pk>/edit/", views.edit_service, name="edit_service"),
    path("services/<int:pk>/delete/", views.delete_service, name="delete_service"),
    path("providers/", views.provider_list, name="provider_list"),

    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="core/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),

    path("bookings/<int:pk>/status/<str:status>/", views.update_booking_status, name="update_booking_status"),
    path("bookings/<int:pk>/cancel/", views.cancel_booking, name="cancel_booking"),
    path("bookings/<int:pk>/review/", views.leave_review, name="leave_review"),
    path("bookings/<int:pk>/delete/", views.delete_booking_record, name="delete_booking_record"),
    path("reviews/<int:pk>/delete/", views.delete_review, name="delete_review"),
]
