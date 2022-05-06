from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("profile", views.profile, name="profile"),
    path("registration/options", views.registration_options, name="registration-options"),
    path(
        "registration/verification",
        views.registration_verification,
        name="registration-verification",
    ),
    path("authentication/options", views.authentication_options, name="authentication-options"),
]
