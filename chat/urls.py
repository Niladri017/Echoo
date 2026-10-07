from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_home, name='chat_home'),
    path(
        'conversation/<int:user_id>/',
        views.conversation,
        name='conversation'
    ),
]