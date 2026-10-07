from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, ProfileForm
from django.contrib.auth.models import User
from posts.models import Notification

def home(request):
    return render(request, 'index.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password')
        
        print("LOGIN USERNAME:", repr(username))
        print("PASSWORD RECEIVED:", bool(password))

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('post_list')

        else:
            return render(request, 'accounts/login.html', {
                'error': 'Invalid username or password.'
            })

    return render(request, 'accounts/login.html')


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            return redirect('login')

    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {
        'form': form
    })


def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def profile(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'form': form
    })
    
@login_required
def follow_user(request, username):
    target_user = User.objects.get(username=username)

    if request.method == 'POST' and target_user != request.user:
        target_profile = target_user.profile
        current_profile = request.user.profile

        if target_profile in current_profile.following.all():
            current_profile.following.remove(target_profile)

        else:
            current_profile.following.add(target_profile)

            Notification.objects.create(
                recipient=target_user,
                sender=request.user,
                notification_type='follow'
            )

    return redirect('user_profile', username=username)

def user_profile(request, username):
    target_user = User.objects.get(username=username)
    target_profile = target_user.profile

    is_following = False

    if request.user.is_authenticated:
        is_following = target_profile in request.user.profile.following.all()

    return render(request, 'accounts/user_profile.html', {
        'profile': target_profile,
        'is_following': is_following,
    })
    
def search_users(request):
    query = request.GET.get('q', '')

    users = User.objects.filter(
        username__icontains=query
    )

    return render(request, 'accounts/search.html', {
        'users': users,
        'query': query,
    })    
    
def followers_list(request, username):
    target_user = User.objects.get(username=username)
    profile = target_user.profile

    followers = profile.followers.all()

    return render(request, 'accounts/followers.html', {
        'profile': profile,
        'users': followers,
        'title': 'Followers',
    })


def following_list(request, username):
    target_user = User.objects.get(username=username)
    profile = target_user.profile

    following = profile.following.all()

    return render(request, 'accounts/following.html', {
        'profile': profile,
        'users': following,
        'title': 'Following',
    })    
    
@login_required
def notifications(request):
    notifications = request.user.notifications.all()

    return render(request, 'accounts/notifications.html', {
        'notifications': notifications
    })    
    
@login_required
def mark_notifications_read(request):
    request.user.notifications.filter(
        is_read=False
    ).update(
        is_read=True
    )

    return redirect('notifications')    