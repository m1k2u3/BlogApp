from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required

from users.models import Profile
# Create your views here.


def registration(request):
    from .forms import RegistrationForm

    form = RegistrationForm()

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            print("Registration success:", user)
            profile = Profile(user=user)
            profile.save()


            return redirect("login")

    return render(request, "registration.html", {"form": form})

def login(request):
    from .forms import LoginForm
    from django.contrib.auth import authenticate, login
    from django.utils.http import url_has_allowed_host_and_scheme
    form = LoginForm()

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                

                next_url = request.POST.get("next") or request.GET.get("next")
                is_secure = url_has_allowed_host_and_scheme(
                    url=next_url,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure(),
                )
                print("Next url: ", next_url, "Is secure: ", is_secure)
                if next_url and is_secure:
                    return redirect(next_url)
                else:
                    return redirect("home")
    
    return render(request, "login.html", {"form": form})


@login_required
def logout(request):
    from django.contrib.auth import logout

    logout(request)

    return redirect("login")

@login_required
def profile(request, username=None):
    from django.contrib.auth.models import User
    from django.shortcuts import get_object_or_404
    from core.models import Post
    from .models import FavouritePosts,Subscription
    user = get_object_or_404(User, username=username) if username else request.user
    posts = Post.objects.filter(author=user).order_by("-created_at").all()
    favourite_posts = FavouritePosts.objects.filter(user=user).all()


    subscribers_count=user.subscribers.count()

    is_subscribed=False
    
    if request.user != user:
        is_subscribed=Subscription.objects.filter(
            subscriber=request.user, author=user
        ).exists()

    rating_sum = 0
    rating_count = 0
    for post in posts:
        rating = post.average_rating()
        if rating > 0:
            rating_sum += rating
            rating_count += 1

    vote_avarage = 0
    if rating_sum > 0:
        vote_avarage = rating_sum / rating_count

    return render(
        request,
        "profile.html",
        {"user": user, "posts": posts, "favourite_posts": favourite_posts, "vote_avarage": vote_avarage, "subscribers_count": subscribers_count, "is_subscribed": is_subscribed},
    )


@login_required
def toggle_favourite_post(request, post_id):
    from django.http import JsonResponse
    from .models import FavouritePosts
    from core.models import Post
    from django.shortcuts import get_object_or_404

    if request.method != "POST":
        return JsonResponse(
            {"status": "error", "error": "Forbidden. Use method POST!"}, status=405
        )

    post = get_object_or_404(Post, id=post_id)
    favourite = FavouritePosts.objects.filter(user=request.user, post=post).first()
    if favourite:
        favourite.delete()
        return JsonResponse({"status": "removed"}, status=200)

    favourite = FavouritePosts(user=request.user, post=post)
    favourite.save()



    return JsonResponse({"status": "saved"}, status=201)

@login_required
def edit_profile(request):
    from django.http import JsonResponse
    from django.contrib.auth.models import User

    if request.method != "POST":
        return JsonResponse({"status": "error", "error": "POST only"}, status=405)

    user = request.user
   
    username = request.POST.get("username", "").strip()
    email = request.POST.get("email", "").strip()

    if username and username != user.username:
        if User.objects.filter(username=username).exists():
            return JsonResponse(
                {"status": "error", "error": "Username already taken"}, status=400
            )

        user.username = username

        if email and email != user.email:
            if User.objects.filter(email=email).exists():
                return JsonResponse(
                    {"status": "error", "error": "Email already taken"}, status=400
            )

        user.email = email

    user.save()

    profile = user.profile
    bio = request.POST.get("bio", "").strip()

    if bio and bio != profile.bio:
        profile.bio = bio

    if "avatar" in request.FILES:
        profile.profile_picture = request.FILES["avatar"]

    profile.save()


    return JsonResponse(
        {
            "status": "success",
            "user": {
                "username": user.username,
                "email": user.email,
                "bio": profile.bio,
                "avatar": profile.profile_picture.url if profile.profile_picture else None,
            },
        }
    )




def toggle_subscription(request, author_id):
    from django.http import JsonResponse
    from .models import Subscription
    from django.contrib.auth.models import User
    from django.shortcuts import get_object_or_404

    if request.method != "POST":
        return JsonResponse(
            {"status": "error", "error": "Forbidden. Use method POST!"},
            status=405
        )

    author = get_object_or_404(User, id=author_id)

    if author == request.user:
        return JsonResponse(
            {"status": "error", "error": "You can not subscribe to yourself!"},
            status=400,
        )

    sub = Subscription.objects.filter(subscriber=request.user, author=author).first()

    if sub:
        sub.delete()
        return JsonResponse({"status": "unsubscribed"}, status=200)
    else:
        Subscription.objects.create(subscriber=request.user, author=author)
        return JsonResponse({"status": "subscribed"}, status=201)