from django.contrib import admin
from .models import User, Student, Parent, Message


class UserAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'username', 'email', 'is_active', 'is_student', 'is_lecturer', 'is_parent', 'is_staff']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_lecturer', 'is_parent', 'is_staff']

    class Meta:
        managed = True
        verbose_name = 'User'
        verbose_name_plural = 'Users'


# class ScoreAdmin(admin.ModelAdmin):
#     list_display = [
#         'student', 'course', 'assignment', 'mid_exam', 'quiz',
#         'attendance', 'final_exam', 'total', 'grade', 'comment'
#     ]



class StudentAdmin(admin.ModelAdmin):
    list_display = ['student', 'Admission_id', 'level', 'session', 'payment']
    list_filter = ['level', 'session', 'department','payment']  # Add filter options
    search_fields = ['student__username', 'Admission_id']  # Add search fields


admin.site.register(Student, StudentAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Parent)
admin.site.register(Message)