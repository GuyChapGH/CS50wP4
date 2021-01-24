import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt

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

            # Pagination. Get page from GET request. Default value equals 1 if no page given
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
        user_posts_list = Post.objects.filter(user_id=user_id).order_by('-timestamp')

        # Getting current user
        current_user = request.user
        # If Follows object for current_user following profile_user exists provide
        # Unfollow button
        if (Follows.objects.filter(follower=current_user, following=profile_user).exists()):
            button_name = "Unfollow"
        # If Follows object does not exist provide Follow button
        else:
            button_name = "Follow"

        # Pagination. Get page from GET request. Default value equals 1 if no page given
        page = request.GET.get('page', 1)

        # Paginate user_posts_list in pages of 10 posts
        paginator = Paginator(user_posts_list, 10)

        # Create page of user_posts. Handling exceptions PageNotAnInteger and EmptyPage
        try:
            user_posts = paginator.page(page)
        except PageNotAnInteger:
            user_posts = paginator.page(1)
        except EmptyPage:
            user_posts = paginator.page(paginator.num_pages)

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
    posts_following_list = p.order_by('-timestamp')

    # Pagination. Get page from GET request. Default value equals 1 if no page given
    page = request.GET.get('page', 1)

    # Paginate posts_following_list in pages of 10 posts
    paginator = Paginator(posts_following_list, 10)

    # Create page of posts_following. Handling exceptions PageNotAnInteger and EmptyPage
    try:
        posts_following = paginator.page(page)
    except PageNotAnInteger:
        posts_following = paginator.page(1)
    except EmptyPage:
        posts_following = paginator.page(paginator.num_pages)

    # Render HTML with data
    return render(request, "network/following.html", {
        "posts_following": posts_following
    })


@csrf_exempt
@login_required
def post(request, post_id):

    # Query for requested post
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Return post contents
    if request.method == "GET":
        # return JsonResponse({"error": "in progress."}, status=400)
        return JsonResponse(post.serialize())

    # Update content of post
    elif request.method == "POST":
        data = json.loads(request.body)
        if data.get("content") is not None:
            post.content = data["content"]
        post.save()
        return JsonResponse({"message": "Post successfully updated."}, status=201)

    # EXPERIMENT to see if likes can be updated. Need to handle failure case.
    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get("likes_flag") is True:
            post.add_like()
        if data.get("likes_flag") is False:
            post.subtract_like()
        post.save()
        return JsonResponse({"message": "Likes successfully updated."}, status=201)

    else:
        return JsonResponse({"error": "GET, PUT or POST request required."}, status=400)


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
