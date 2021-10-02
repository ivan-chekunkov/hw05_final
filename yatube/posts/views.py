from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.shortcuts import redirect, render, get_object_or_404
from .models import Comment, Follow, Post, Group, User
from .forms import PostForm, CommentForm
User = get_user_model()


def index(request):
    post_cache = cache.get('post')
    if not post_cache:
        post_list = Post.objects.all()
        cache.set('post', post_list, 20)
        post_cache = post_list
    paginator = Paginator(post_cache, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    profile_post = author.posts.all()
    paginator = Paginator(profile_post, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    user = request.user
    following = user.is_authenticated and author.following.exists()
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comment = Comment.objects.filter(post=post)
    form = CommentForm()
    context = {
        'post': post,
        'comments': comment,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(instance=post)
    if request.user != post.author:
        return redirect('posts:post_detail', post.pk)
    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('posts:post_detail', post.pk)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_create(request):
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None
        )
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', post.author)
    context = {
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    author_list = Follow.objects.filter(user=request.user)
    f = []
    for i in range(len(author_list)):
        f.append(author_list[i].author.id)
    post_list1 = Post.objects.filter(author_id__in=f)
    paginator = Paginator(post_list1, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = User.objects.get(username=request.user)
    author = User.objects.get(username=username)
    if user == author:
        return redirect('posts:profile', username=username)
    if Follow.objects.filter(user=user, author=author):
        return redirect('posts:profile', username=username)
    follow = Follow()
    follow.user = user
    follow.author = author
    follow.save()
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    user = User.objects.get(username=request.user)
    author = User.objects.get(username=username)
    unfollow = Follow.objects.filter(user=user, author=author)
    if not unfollow:
        return redirect('posts:profile', username=username)
    unfollow.delete()
    return redirect('posts:profile', username=username)
