from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    path('search/', views.search_users, name='search_users'),
    path('user/<str:username>/followers/', views.followers_list, name='followers_list'),
    path('user/<str:username>/following/', views.following_list, name='following_list'),
    path('notifications/', views.notifications, name='notifications'),
    path(
    'notifications/read/',
    views.mark_notifications_read,
    name='mark_notifications_read'
),
]  