
from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("following", views.FollowingView.as_view(), name="following"),
    path("like/<int:id>", views.like, name="like"),
    path("profile/<int:id>", views.ProfileView.as_view(), name="profile"),
    path("follow/<int:id>", views.follow, name="follow"),
    path("update/<int:id>", views.update, name="update"),
]