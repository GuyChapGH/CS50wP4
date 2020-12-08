from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse

from .models import User
from .models import Post
from .models import Follows


def index(request):
    if request.user.is_authenticated:
        if request.method == "POST":

            # Get values for current user and post content from form
            current_user = request.user
            content = request.POST["content"]

            # Create new post and save to database
            p = Post(user=current_user, content=content)
            p.save()

            # Return to index page
            return HttpResponseRedirect(reverse("index"))

        else:
            # If accessed by GET request return to index page. (if use redirect here get infinite loop??)

            # Get all posts.
            posts = Post.objects.all().order_by('-timestamp')

            return render(request, "network/index.html", {
                "posts": posts
            })

    else:
        # If user not logged in redirect to login page
        return render(request, "network/login.html")


def profile(request, user_id):
    if request.method == "POST":
        # Remove this duplicate when ready with form handling code
        user_posts = Post.objects.filter(user_id=user_id).order_by('-timestamp')
        return render(request, "network/profile.html", {
            "user_posts": user_posts
        })
    else:
        # Getting user object to provide username of profile
        try:
            # Get user object based on user_id
            profile_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise Http404("User not found.")

        # Count the number of followers belonging to the profile user
        followers_count = Follows.objects.filter(following_id=user_id).count()

        # Count the number of users that the profile user is following
        following_count = Follows.objects.filter(follower_id=user_id).count()

        # Find posts belonging to the profile user
        user_posts = Post.objects.filter(user_id=user_id).order_by('-timestamp')

        # Controlling display of Follow and Unfollow buttons
        # flag_follow = "disabled"
        # flag_unfollow = "disabled"

        current_user = request.user
        if (Follows.objects.filter(follower=current_user, following=profile_user).exists()):
            button_name = "Unfollow"
        else:
            button_name = "Follow"

        # Render HTML with data
        return render(request, "network/profile.html", {
            # "flag_follow": flag_follow,
            # "flag_unfollow": flag_unfollow,
            "button_name": button_name,
            "profile_user": profile_user,
            "followers_count": followers_count,
            "following_count": following_count,
            "user_posts": user_posts
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
