from .models import Message


def unread_message_count(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'student'):
            unread_count = Message.objects.filter(students=request.user.student, is_read=False).count()
            if unread_count > 9:
                unread_count = '+9'
        else:
            # User is authenticated but not a student
            unread_count = ''
    else:
        # Guest users have no unread messages
        unread_count = ''

    return {'unread_message_count': unread_count}
