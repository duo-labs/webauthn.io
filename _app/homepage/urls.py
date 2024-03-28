from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("logout", views.logout, name="logout"),
    path("registration/options", views.registration_options, name="registration-options"),
    path(
        "registration/verification",
        views.registration_verification,
        name="registration-verification",
    ),
    path(
        "authentication/options",
        views.authentication_options,
        name="authentication-options",
    ),
    path(
        "authentication/verification",
        views.authentication_verification,
        name="authentication-verification",
    ),
    path(
        "credential/<credential_id>/delete",
        views.credential_delete,
        name="credential-delete",
    ),
    path(
        ".well-known/apple-app-site-association",
        views.apple_app_site_association,
        name="apple-app-site-association",
    ),
]
