from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User

from .models import Conversation, Message


@login_required
def chat_home(request):

    following = request.user.profile.following.all()

    conversations = Conversation.objects.filter(
        participants=request.user
    ).prefetch_related(
        'participants',
        'messages'
    ).order_by('-created_at')

    conversation_user_ids = []

    for conversation in conversations:

        for participant in conversation.participants.all():

            if participant != request.user:
                conversation_user_ids.append(
                    participant.id
                )

    following_without_conversations = following.exclude(
        user__id__in=conversation_user_ids
    )

    # ==========================================
    # UNREAD COUNT FOR EACH CONVERSATION
    # ==========================================

    for conversation in conversations:

        conversation.unread_count = conversation.messages.filter(
            is_read=False
        ).exclude(
            sender=request.user
        ).count()

    # ==========================================
    # GLOBAL UNREAD MESSAGE COUNT
    # ==========================================

    unread_messages_count = Message.objects.filter(
        conversation__participants=request.user,
        is_read=False
    ).exclude(
        sender=request.user
    ).count()

    return render(
        request,
        'chat/chat_home.html',
        {
            'following': following_without_conversations,
            'conversations': conversations,
            'unread_messages_count': unread_messages_count,
        }
    )


@login_required
def conversation(request, user_id):

    # ==========================================
    # GET USERS
    # ==========================================

    other_user = get_object_or_404(
        User,
        id=user_id
    )

    current_user = request.user


    # ==========================================
    # FIND EXISTING CONVERSATION
    # ==========================================

    chat = Conversation.objects.filter(
        participants=current_user
    ).filter(
        participants=other_user
    ).first()


    # ==========================================
    # CREATE NEW CONVERSATION
    # ==========================================

    if not chat:

        # Only allow starting a NEW conversation
        # with someone the current user follows.

        if not current_user.profile.following.filter(
            user=other_user
        ).exists():

            return redirect('chat_home')


        chat = Conversation.objects.create()

        chat.participants.add(
            current_user,
            other_user
        )


    # ==========================================
    # MARK INCOMING MESSAGES AS READ
    # ==========================================

    Message.objects.filter(
        conversation=chat,
        is_read=False
    ).exclude(
        sender=current_user
    ).update(
        is_read=True
    )


    # ==========================================
    # NORMAL POST MESSAGE
    # ==========================================

    if request.method == 'POST':

        text = request.POST.get(
            'text',
            ''
        ).strip()

        if text:

            Message.objects.create(
                conversation=chat,
                sender=current_user,
                text=text
            )

        return redirect(
            'conversation',
            user_id=other_user.id
        )


    # ==========================================
    # OPEN CONVERSATION
    # ==========================================

    return render(
        request,
        'chat/conversation.html',
        {
            'conversation': chat,
            'other_user': other_user,
        }
    )