from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User
from .models import Post
from .models import Likes


def index(request):
    if request.user.is_authenticated:
        if request.method == "POST":

            # Get values for current user and post content from form
            current_user = request.user
            content = request.POST["content"]

            # Create new post and save to database
            p = Post(user=current_user, content=content)
            p.save()

            # Create corresponding Likes object and save to database
            like = Likes(post=p)
            like.save()

            # Return to index page
            return HttpResponseRedirect(reverse("index"))

        else:
            # If accessed by GET request return to index page. (if use redirect here get infinite loop??)

            # N.B. This call seems the wrong way
            # round. Should be querying the Post objects and related Likes rather
            # Likes and related posts. It is a result of how I defined the models but
            # the relationship between Post and Likes is OneToOne so it doesnt actually matter
            # for now.

            # Get all Likes and corresponding posts.
            posts_likes = Likes.objects.select_related('post')

            return render(request, "network/index.html", {
                "posts_likes": posts_likes
            })

    else:
        # If user not logged in redirect to login page
        return render(request, "network/login.html")


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
