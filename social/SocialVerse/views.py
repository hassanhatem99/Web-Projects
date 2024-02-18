import datetime
import pytz 
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from django.db.models import Subquery, OuterRef



from .models import User, Post, Comment, LikedPost, PostImage
from .forms import CommentForm, PostForm, Search, UserForm
import geoip2.database


from geopy.geocoders import Nominatim

from .time_utils import get_timezone_by_ip, set_timezone





@set_timezone
def index(request):
    user = request.user
    if user.is_authenticated:
        # Retrieve the user's following
        following_list = user.following.all()

        # Retrieve posts and other data
        posts = Post.objects.all().order_by('-time_created')
        following_posts = []
        for post in posts:
            post.time_created = timezone.localtime(post.time_created)
            if user.follows(post.poster) or post.poster.username == user.username:
                following_posts.append(post)

        liked_posts = LikedPost.objects.filter(user=user, post__in=posts).values_list('post_id', flat=True)

        if request.method == "POST":
            form = Search(request.POST)
            if form.is_valid():
                query = form.cleaned_data["query"]
                return redirect(f"/search_results/{query}")
            else:
                form = Search()        
        else:
            return render(request, "SocialVerse/index.html", {
                "posts": posts,
                "user": user,
                "liked_posts": liked_posts,
                "search_form": Search,
                "search_icon": "🔎",
                "following_list": following_list,  # Pass the following list as a context variable
                'following_posts': following_posts,
            })
    else:
        return redirect("login")



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "SocialVerse/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "SocialVerse/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        form = UserForm(request.POST, request.FILES)

        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:
            return render(request, "SocialVerse/register.html", {
                "message": "Passwords must match.",
                "PPform": UserForm
            })

        # Attempt to create a new user
        try:
            User = get_user_model()
            user = User.objects.create_user(username, email, password)

            # Set the default profile picture if the form doesn't include one
            if not request.FILES.get('prof_pic'):
                user.prof_pic = 'images/default.jpg'

            if form.is_valid():
                if 'prof_pic' in request.FILES:
                    user.prof_pic = request.FILES['prof_pic']
                user.save()
        except IntegrityError:
            return render(request, "SocialVerse/register.html", {
                "message": "Username already taken.",
                "PPform": UserForm
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "SocialVerse/register.html", {
            "PPform": UserForm
        })





@set_timezone
@login_required(login_url='/login')

def liked_posts(request):
    user = request.user
    if user.is_authenticated:
        liked_posts = LikedPost.objects.filter(user=user).order_by('-timestamp')
        posts = [post.post for post in liked_posts]
        if request.method == "POST":
            form = Search(request.POST)
            if form.is_valid():
                query = form.cleaned_data["query"]
                return redirect(f"/search_results/{query}")
            else:
                form = Search()
        return render(request, "SocialVerse/liked_posts.html", {
            "posts": posts,
            "liked_posts": liked_posts,
            "search_form": Search,
            "search_icon": "🔎"
        })

  


@set_timezone
@login_required(login_url='/login')

def comment(request, post_id):
    user = request.user
    posts = Post.objects.all().order_by('-time_created')
    post = Post.objects.get(id=post_id)
    comments = list(Comment.objects.filter(post=post))[::-1]        
    if request.user.is_authenticated:
        username = user.username
        liked_posts = LikedPost.objects.filter(user=user, post__in=posts).values_list('post_id', flat=True)
    if request.method == "POST":
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                text = form.cleaned_data["text"]
                new_comment = Comment(text=text, commentor=username, post=post, time_created = timezone.now())
                new_comment.save()
                return redirect(f"/{post_id}/comment")
        else:
            return redirect("login")
    else:
        form = CommentForm()
        return render(request, "SocialVerse/comment.html",{
            "post": post,
            "form": form,
            "comments": comments,
            "liked_posts": liked_posts
    })



@set_timezone
@login_required(login_url='/login')
def like(request, post_id):
    post = Post.objects.get(id=post_id)
    user = request.user

    # Check if the WatchlistItem already exists
    liked_post, created = LikedPost.objects.get_or_create(user=user, post=post)

    if created:
        pass

    # Redirect to the previous URL with the listing anchor
    previous_url = request.META.get('HTTP_REFERER')
    if previous_url:
        return redirect(previous_url + '#post-' + str(post.id))
    else:
        return redirect('index')


@set_timezone
@login_required(login_url='/login')
def unlike(request, post_id):
    post = Post.objects.get(id=post_id)
    user = request.user

    # Remove the watchlist item associated with the user and listing
    liked_post = LikedPost.objects.get(user=user, post=post)
    liked_post.delete()

    # Redirect to the previous URL with the listing anchor
    previous_url = request.META.get('HTTP_REFERER')
    if previous_url:
        return redirect(previous_url + '#post-' + str(post.id))
    else:
        return redirect('index')



@set_timezone
@login_required(login_url='/login')
def create_post(request):
    user = request.user
    if request.method == "POST":
        if user.is_authenticated:
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                post = form.save(commit=False)  # Save the form data but don't commit it to the database yet
                post.poster = user  # Set the seller field to the current user
                post.save()  # Save the listing with the updated fields
                images = request.FILES.getlist('image')  # Get the list of uploaded images
                for image in images:
                    PostImage.objects.create(post=post, image=image)  # Create a ListingImage object for each image
                return render(request, "SocialVerse/created.html", {
                    "post": post
                })
        else:
            return redirect("login")
    else:
        form = PostForm()
    return render(request, "SocialVerse/create_post.html", {
        "form": form
    })




@set_timezone
@login_required(login_url='/login')

def created(request):
    if request.method == "POST":
            form = Search(request.POST)
            if form.is_valid():
                query = form.cleaned_data["query"]
                return redirect(f"/search_results/{query}")
            else:
                form = Search()
    return render(request, "SocialVerse/created.html")



@set_timezone
@login_required(login_url='/login')
def delete_post(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.user.is_authenticated:
        username = request.user.username
    if username == post.poster:
        pass
        #TODO Delete post from database

    return render(request, "SocialVerse/deleted.html", {
        "post": post
    })  # Redirect to a success page
    


@set_timezone
@login_required(login_url='/login')
def my_profile(request):
    user = request.user
    posts = Post.objects.filter(poster=user).order_by("-time_created")
    if user.is_authenticated:
        liked_posts = LikedPost.objects.filter(user=user, post__in=posts).values_list('post_id', flat=True)
        
        if request.method == "POST":
            form = Search(request.POST)
            if form.is_valid():
                query = form.cleaned_data["query"]
                return redirect(f"/search_results/{query}")
            else:
                form = Search()
        return render(request, "SocialVerse/my_profile.html", {
            "posts": posts,
            "user": user,
            "liked_posts": liked_posts,
            "search_form": Search,
            "search_icon": "🔎"
        })
    

@set_timezone
@login_required(login_url='/login')
def user_profile(request, username):
    user = request.user
    visited_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(poster=visited_user).order_by("-time_created")

    if not request.user.follows(visited_user):
        follow_button = "Follow"
    else:
        follow_button = "Unfollow"
    if user.is_authenticated:
        liked_posts = LikedPost.objects.filter(user=user, post__in=posts).values_list('post_id', flat=True)
        return render(request, "SocialVerse/user_profile.html", {
            "posts": posts,
            "user": user,
            "liked_posts": liked_posts,
            "visited_user": visited_user,
            "search_form": Search,
            "search_icon": "🔎",
            "follow_button": follow_button
        })



@set_timezone

def search_results(request, query):
    user = request.user
    
    # Split the query into individual words
    query_words = query.split()
    
    # Create a Q object to accumulate the filter conditions
    filter_conditions = Q()
    for word in query_words:
        filter_conditions &= (Q(poster__username__icontains=word) | Q(caption__icontains=word))
    
    # Apply the filter conditions to the Post queryset
    posts = Post.objects.filter(filter_conditions).order_by("-time_created")
    
    liked_posts = []
    if user.is_authenticated:
        liked_posts = LikedPost.objects.filter(user=user, post__in=posts).values_list('post_id', flat=True)

    if request.method == "POST":
        form = Search(request.POST)
        if form.is_valid():
            query = form.cleaned_data["query"]
            return redirect(f"/search_results/{query}")
    else:
        form = Search(initial={"query": query})

    return render(request, "SocialVerse/search_results.html", {
        "posts": posts,
        "liked_posts": liked_posts,
        "query": query,
        "search_form": form,
        "search_icon": "🔎"
    })



@login_required
def follow(request, username):
    user_to_follow = User.objects.get(username=username)

    # Check if the user doesn't follow the target user
    if not request.user.follows(user_to_follow):
        request.user.follow(user_to_follow)

    return redirect(f'/user_profile/{username}', user=user_to_follow)


@login_required
def unfollow(request, username):
    user_to_unfollow = User.objects.get(username=username)

    # Check if the user doesn't follow the target user
    if request.user.follows(user_to_unfollow):
        request.user.unfollow(user_to_unfollow)

    return redirect(f'/user_profile/{username}', user=user_to_unfollow)