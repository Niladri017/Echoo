from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.models import User

from .models import Post, Like, Comment, Notification


def post_list(request):
    if request.user.is_authenticated:
        following_users = request.user.profile.following.all()

        posts = Post.objects.filter(
            Q(author=request.user) |
            Q(author__profile__in=following_users)
        ).order_by('-created_at')

    else:
        posts = Post.objects.all().order_by('-created_at')

    return render(request, 'posts/post_list.html', {
        'posts': posts
    })


@login_required
def like_post(request, post_id):
    post = Post.objects.get(id=post_id)

    like = Like.objects.filter(
        user=request.user,
        post=post
    ).first()

    if like:
        like.delete()
        liked = False

    else:
        Like.objects.create(
            user=request.user,
            post=post
        )

        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                sender=request.user,
                notification_type='like',
                post=post
            )

        liked = True

    return JsonResponse({
        'liked': liked,
        'likes': post.like_set.count()
    })


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(id=post_id)

    if request.method == 'POST':
        text = request.POST.get('text')

        if text:
            Comment.objects.create(
                user=request.user,
                post=post,
                text=text
            )

            if post.author != request.user:
                Notification.objects.create(
                    recipient=post.author,
                    sender=request.user,
                    notification_type='comment',
                    post=post
                )

    return redirect('post_list')


@login_required
def create_post(request):
    if request.method == 'POST':
        caption = request.POST.get('caption')
        image = request.FILES.get('image')

        if caption:
            Post.objects.create(
                author=request.user,
                caption=caption,
                image=image
            )

        return redirect('post_list')


@login_required
def delete_post(request, post_id):
    post = Post.objects.get(id=post_id)

    if request.method == 'POST' and post.author == request.user:
        post.delete()

    return redirect('post_list')


@login_required
def edit_post(request, post_id):
    post = Post.objects.get(id=post_id)

    if post.author != request.user:
        return redirect('post_list')

    if request.method == 'POST':
        caption = request.POST.get('caption')
        image = request.FILES.get('image')

        if caption:
            post.caption = caption

        if image:
            post.image = image

        post.save()

        return redirect('post_list')

    return render(request, 'posts/edit_post.html', {
        'post': post
    })