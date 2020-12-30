from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
            posts_list = Post.objects.all().order_by('-timestamp')

            # Get page from GET request. Default value equals 1 if no page given
            page = request.GET.get('page', 1)

            # Paginate posts_list in pages of 10 posts
            paginator = Paginator(posts_list, 10)

            # Create page of posts. Handling exceptions PageNotAnInteger and EmptyPage
            try:
                posts = paginator.page(page)
            except PageNotAnInteger:
                posts = paginator.page(1)
            except EmptyPage:
                posts = paginator.page(paginator.num_pages)

            # Render HTML with data
            return render(request, "network/index.html", {
                "posts": posts
            })

    else:
        # If user not logged in redirect to login page
        return render(request, "network/login.html")


def profile(request, user_id):

    if request.method == "POST":
        current_user = request.user
        # Getting profile_user object
        try:
            # Get user object based on user_id
            profile_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise Http404("User not found.")

        if (Follows.objects.filter(follower=current_user, following=profile_user).exists() and request.POST.get("toggle")):
            # Retrieving Follows object for current_user following profile_user
            f = Follows.objects.get(follower=current_user, following=profile_user)
            # Delete from database
            f.delete()

        elif (not Follows.objects.filter(follower=current_user, following=profile_user).exists() and request.POST.get("toggle")):
            # Creating Follows object for current_user following profile_user
            f = Follows(follower=current_user, following=profile_user)
            # Commit to database
            f.save()

        return HttpResponseRedirect(reverse("profile", args=(user_id,)))

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

        # Getting current user
        current_user = request.user
        # If Follows object for current_user following profile_user exists provide
        # Unfollow button
        if (Follows.objects.filter(follower=current_user, following=profile_user).exists()):
            button_name = "Unfollow"
        # If Follows object does not exist provide Follow button
        else:
            button_name = "Follow"

        # Render HTML with data
        return render(request, "network/profile.html", {
            "button_name": button_name,
            "current_user": current_user,
            "profile_user": profile_user,
            "followers_count": followers_count,
            "following_count": following_count,
            "user_posts": user_posts
        })


@login_required
def following(request):
    # Get current user
    current_user = request.user

    # Create empty queryset
    p = Post.objects.none()

    # Iterate through queryset
    for user in Follows.objects.filter(follower=current_user):

        # Concatenate posts from each user
        p = Post.objects.filter(user=user.following) | p

    # Order posts in reverse chronological order
    posts_following = p.order_by('-timestamp')

    # Render HTML with data
    return render(request, "network/following.html", {
        "posts_following": posts_following
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
