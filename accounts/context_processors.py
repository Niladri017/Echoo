from chat.models import Message


def notifications_count(request):
    if request.user.is_authenticated:

        unread_count = request.user.notifications.filter(
            is_read=False
        ).count()

        unread_messages_count = Message.objects.filter(
            conversation__participants=request.user,
            is_read=False
        ).exclude(
            sender=request.user
        ).count()

    else:
        unread_count = 0
        unread_messages_count = 0

    return {
        'unread_notifications_count': unread_count,
        'unread_messages_count': unread_messages_count,
    }