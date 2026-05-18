from urllib import request

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from core.emails import send_new_post_email





@login_required
def post_details(request, post_id):
    from .models import Post,Comment
    from django.shortcuts import get_object_or_404,redirect
    from .forms import CommentForm
    from django.shortcuts import redirect
    from django.urls import reverse
    from users.models import FavouritePosts
    # if  not request.user.is_authenticated:
    #     return redirect("login")
    # post = Post.objects.get(id=post_id)
    post = get_object_or_404(Post, id=post_id)
    posts_by_category = Post.objects.filter(category=post.category).exclude(id=post.id).all()
    form=CommentForm()
    
    if request.method == "POST":
        form=CommentForm(request.POST)
        if form.is_valid():

            newComments = form.save(commit=False)
            newComments.author = request.user
            newComments.post=post
            newComments.save()

    comments=Comment.objects.order_by("-created_at").all()

    if not request.user.is_authenticated:
            next_url = request.get_full_path()
            login_url = f"{reverse("login")}?next={next_url}"
            return redirect(login_url)



    is_favourite = False
    if request.user.is_authenticated:
        is_favourite = FavouritePosts.objects.filter(
            user=request.user, post=post
        ).exists()
        
    return render(request, "post_details.html", {'post': post , 'posts_by_category':posts_by_category,'comments':comments,'form':form,"is_favourite": is_favourite})


from django.contrib.auth.decorators import login_required


@login_required
def post_creation(request):
    from .forms import PostForm
    from django.shortcuts import redirect

    form = PostForm()
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():

            newPost = form.save(commit=False)
            newPost.author = request.user

            newPost.save()

            return redirect("all_posts")

    return render(request, "create_post.html", {"form": form})

# @login_required
# def delete_comment(request, comment_id):
#     from django.shortcuts import get_object_or_404
#     from .models import Comment
#     from django.http import JsonResponse, HttpResponse

#     if request.method == "DELETE":
#         comment = get_object_or_404(Comment, id=comment_id)

#         if comment.author != request.user:
#             return JsonResponse(
#                 {"error": "Only comment author can delete it!"}, status=400
#             )

#         comment.delete()

#         return HttpResponse(status=204)
#     else:
#         return JsonResponse({"error": "Method not allowed"}, status=405)
    


@login_required
def delete_post(request, post_id):
    from django.shortcuts import get_object_or_404
    from .models import Post
    from django.http import JsonResponse, HttpResponse

    if request.method == "DELETE":
        post = get_object_or_404(Post, id=post_id)

        if post.author != request.user:
            return JsonResponse(
                {"error": "Only comment author can delete it!"}, status=400
            )

        post.delete()

        return HttpResponse(status=204)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)


@login_required
def edit_post(request, post_id):
    from .forms import PostForm
    from .models import Post
    from django.shortcuts import redirect, get_object_or_404
    from django.http import Http404
    
    post=get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        raise Http404("No Post found with current id!")

    form = PostForm(instance=post)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():

            newPost = form.save(commit=False)
            newPost.author = request.user

            newPost.save()

            return redirect("post_details", post_id=post.id )

    return render(request, "create_post.html", {"form": form})


def index(request):
    from .models import Post, Category
    from django.db.models import Avg
    
    posts = Post.objects.order_by("-created_at").all()
    categories = Category.objects.order_by("-created_at").all()
    
    top_post=Post.objects.annotate(avg_rating=Avg("comments__rating")).order_by("-avg_rating").first()
    # send_new_post_email(top_post, 'golubmax0@gmail.com')

    
    return render(
        request, "index.html", {"posts": posts[0:5], "categories": categories, "top_post":top_post}
    )

def all_posts(request):
    from .models import Post, Category
    from django.db.models import Q
    from django.core.paginator import Paginator

    query = request.GET.get("search", "")
    category_id = request.GET.get("category_id", "")
    posts = Post.objects.order_by("-created_at").all()

    if query:
        posts = posts.filter(
            Q(title__icontains=query)
            | Q(short_description__icontains=query)
            | Q(content__icontains=query)
            | Q(category__title__icontains=query)
            | Q(author__username__icontains=query)
        )

    if category_id:
        category = Category.objects.filter(id=category_id).first()
        if category:
            category_id=int(category_id)
            posts = posts.filter(category=category)
    paginator = Paginator(posts, 2)
    page_number = request.GET.get("page", 1)
    page_objs = paginator.get_page(page_number)

    categories = Category.objects.order_by("-created_at").all()

    return render(
        request,
        "post.html",
        {"posts": page_objs, "categories": categories, "query": query, "category_id": category_id},
    )