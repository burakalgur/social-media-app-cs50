from typing import Any, Dict
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import ListView
from .forms import PostForm
from django.urls import reverse
from django.http import JsonResponse, HttpResponseBadRequest
from datetime import datetime


from .models import User, Post, UserFollow


class IndexView(ListView):
    template_name = 'network/index.html'
    model = Post
    ordering = ['-timestamp']
    context_object_name = 'posts'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post_form"] = PostForm()
        return context

    def post(self, request):
        form = PostForm(request.POST)

        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("login"))

        if form.is_valid():
            post = form.save(commit=False)
            post.owner = request.user
            post.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/index.html", {
                "post_form": form
            })


class ProfileView(ListView):
    template_name = 'network/profile_page.html'
    model = Post
    context_object_name = 'posts'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        user_id = self.kwargs['id']
        profile = User.objects.get(id=user_id)
        isFollowing = UserFollow.objects.filter(
            following__id=user_id, follower__id=self.request.user.id).exists()

        context = super().get_context_data(**kwargs)
        context["username"] = profile
        context["followers"] = profile.followers.count()
        context["following"] = profile.following.count()
        context["isOwner"] = self.request.user.id == user_id
        context["isFollowing"] = isFollowing
        return context

    def get_queryset(self):
        user_id = self.kwargs['id']
        return Post.objects.filter(owner=user_id).order_by('-timestamp')


class FollowingView(ListView):
    template_name = 'network/following.html'
    model = Post
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        user_id = self.request.user.id
        followed_users = UserFollow.objects.filter(
            follower__id=user_id).values_list('following', flat=True)
        return Post.objects.filter(owner__in=followed_users).order_by('-timestamp')



def like(request, id):
    try:
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("login"))

        user = User.objects.get(id=request.user.id)
        post = Post.objects.get(id=id)
        like = post.likes.filter(liked_posts=post)
        if like:
            post.likes.remove(user)
        else:
            post.likes.add(user)

        total_likes = post.likes.count()
    except KeyError:
        return HttpResponseBadRequest("Bad Request: no like chosen")
    return JsonResponse({
        "post": id, "total_likes": total_likes, "liked": not like
    })


def follow(request, id):
    try:
        user = User.objects.get(id=request.user.id)
        followed_user = User.objects.get(id=id)

        if (user.id == followed_user.id):
            return HttpResponseBadRequest("Bad Request: You cannot follow yourself")

        isFollowing = UserFollow.objects.filter(
            following__id=id, follower__id=request.user.id).exists()
        if isFollowing:
            UserFollow.objects.filter(
                following__id=id, follower__id=request.user.id).delete()
        else:
            userFollow = UserFollow.objects.create(
                following=followed_user, follower=user)
            userFollow.save()

        total_followers = followed_user.followers.count()
    except KeyError:
        return HttpResponseBadRequest("Bad Request: no like chosen")
    return JsonResponse({
        "followed_user": id, "total_followers": total_followers, "followed": not isFollowing
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def update(request, id):
    post = Post.objects.get(id=id)

    if request.user.id != post.owner.id:
        return HttpResponseBadRequest("Bad Request: You cannot edit this post")

    if request.method == "POST":
        print(request.POST)
        content = request.POST.get("content")
        if (content is None or content == "" or content.isspace()):
            return HttpResponseBadRequest("Bad Request: No content provided")

        post.content = content
        post.save()
        return JsonResponse({"message": "Post updated successfully", "content": post.content}, status=200)

    return JsonResponse({"error": "Bad request"}, status=400)
