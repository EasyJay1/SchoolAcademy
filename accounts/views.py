from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import (
    PasswordChangeForm
)
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.views import PasswordResetView
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy

from django.views.generic import View
from django.http import JsonResponse
from .models import Message
from django.contrib.auth import authenticate
from course.models import Course
from result.models import TakenCourse
from app.models import Session, Semester
from .forms import StaffAddForm, StudentAddForm, ProfileUpdateForm, MessageForm, EmailValidationOnForgotPassword
from .models import Student
from .models import Parent
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.shortcuts import  get_object_or_404
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .decorators import admin_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import ListView
from .models import User  # Update this import to your User model
from .forms import StudentFilterForm




@login_required
def generate_pdf(request):
    template = get_template('accounts/download_form.html')
    try:
        parent = Parent.objects.get(user=request.user)
    except Parent.DoesNotExist:
        return redirect('add_parent')  # Replace 'parent_form' with your actual URL name for the parent form
    parent = Parent.objects.get(user=request.user)
    users_with_same_email = Parent.objects.filter(email_p=parent.email_p).exclude(user=request.user)
    current_session = Session.objects.filter(is_current_session=True).first()
    current_semester = Semester.objects.filter(is_current_semester=True, session=current_session).first()
    all_notes = Parent.objects.filter(user=request.user)
    if request.user.is_student:
        student = Student.objects.get(student=request.user)
        classes = Student.objects.get(student__pk=request.user.id)
        try:
            parent = Parent.objects.get(student=classes)
        except:
            parent = "no parent set"
        courses = TakenCourse.objects.filter(
            student__student__id=request.user.id, course__level=classes.level
        )

    if request.user.is_lecturer:
        courses = Course.objects.filter(
            allocated_course__lecturer__pk=request.user.id
        ).filter(semester=current_semester)

    # Add the necessary context data here
    context = {
        'user': request.user,
        'current_semester': current_semester,  # Add current semester data if needed
        'current_session': current_session,  # Add current session data if needed
        'all_notes': all_notes,  # Add all_notes data if needed
        'users_with_same_email': users_with_same_email,  # Add users_with_same_email data if needed
        # Add other context data as needed
        "parent": parent,
        "student": student,
        "courses": courses,
        "level": classes,

    }

    html = template.render(context)

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{request.user.first_name} {request.user.last_name}.pdf"'

    # Generate the PDF from the HTML content
    pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)

    # Check if PDF generation was successful
    if pisa_status.err:
        return HttpResponse('PDF generation error')

    return response


# Define a link_callback function if you have any external resources in your template
def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those resources.
    """
    # Insert logic to determine the full system path for your resource here.
    return uri



def validate_username(request):
    username = request.GET.get("username", None)
    data = {"is_taken": User.objects.filter(username__iexact=username).exists()}
    return JsonResponse(data)


def register(request):
    if request.method == "POST":
        form = StudentAddForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Log the user in after successful registration
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)

            messages.success(request, f"{username} created successfully. \nComplete your Registration Process!")
            return redirect('edit_profile')  # Redirect to the login page
        else:
            messages.error(request, f"Something is not correct, please fill all fields correctly.")
    else:
        form = StudentAddForm(request.POST)
    return render(request, "registration/register.html", {"form": form})




@login_required
def profile(request):
    try:
        parent = Parent.objects.get(user=request.user)
    except Parent.DoesNotExist:
        return redirect('add_parent')  # Replace 'parent_form' with your actual URL name for the parent form
    parent = Parent.objects.get(user=request.user)
    users_with_same_email = Parent.objects.filter(email_p=parent.email_p).exclude(user=request.user)
    current_session = Session.objects.filter(is_current_session=True).first()
    current_semester = Semester.objects.filter(is_current_semester=True, session=current_session).first()
    all_notes = Parent.objects.filter(user=request.user)

    if request.user.is_student:
        student = Student.objects.get(student=request.user)

    if request.user.is_lecturer:
        courses = Course.objects.filter(
            allocated_course__lecturer__pk=request.user.id
        ).filter(semester=current_semester)
        return render(
            request,
            "accounts/profile.html",
            {
                'users_with_same_email': users_with_same_email,
                "title": request.user.get_full_name,
                "courses": courses,
                "current_session": current_session,
                "current_semester": current_semester,
                "student": student,
                "all_notes":all_notes,
            },
        )
    elif request.user.is_student:
        classes = Student.objects.get(student__pk=request.user.id)
        try:
            parent = Parent.objects.get(student=classes)
        except:
            parent = "no parent set"
        courses = TakenCourse.objects.filter(
            student__student__id=request.user.id, course__level=classes.level
        )
        context = {
            "title": request.user.get_full_name,
            "parent": parent,
            "student": student,
            "courses": courses,
            "level": classes,
            'users_with_same_email': users_with_same_email,
            "all_notes": all_notes,
            "current_session": current_session,
            "current_semester": current_semester,
        }
        return render(request, "accounts/profile.html", context)
    else:
        staff = User.objects.filter(is_lecturer=True)
        return render(
            request,
            "accounts/profile.html",
            {
                "title": request.user.get_full_name,
                "staff": staff,
                "current_session": current_session,
                "current_semester": current_semester,
                "all_notes": all_notes,
                'users_with_same_email': users_with_same_email,
            },
        )


@login_required
@admin_required
def profile_single(request, id):
    """Show profile of any selected user and handle course assignment and dropping for superusers"""
    if request.user.id == id:
        return redirect("/profile/")
    current_session = Session.objects.filter(is_current_session=True).first()
    current_semester = Semester.objects.filter(
        is_current_semester=True, session=current_session
    ).first()
    user = User.objects.get(pk=id)
    similar_users = User.objects.filter(email=user.email)

    if request.method == 'POST':
        if request.user.is_superuser:
            selected_course_ids = request.POST.getlist('selected_courses')
            student = Student.objects.get(student__pk=id)
            for course_id in selected_course_ids:
                course = Course.objects.get(pk=course_id)
                try:
                    obj = TakenCourse.objects.get(student=student, course=course)
                    obj.delete()
                    messages.success(request, f'Course {course.title} dropped successfully for {user.get_full_name()}')
                except TakenCourse.DoesNotExist:
                    messages.warning(request, f'Course {course.title} was not registered for {user.get_full_name()}')

            return redirect('profile_single', id=id)  # Redirect to the same profile page after processing the form.

    if user.is_lecturer:
        courses = Course.objects.filter(allocated_course__lecturer__pk=id).filter(
            semester=current_semester
        )
        context = {
            "title": user.get_full_name,
            "user": user,
            "user_type": "Lecturer",
            "courses": courses,
            "current_session": current_session,
            "current_semester": current_semester,
            "similar_users": similar_users,  # Pass similar users to the context
        }
    elif user.is_student:
        student = Student.objects.get(student__pk=id)
        courses = TakenCourse.objects.filter(
            student__student__id=id, course__level=student.level
        )
        context = {
            "title": user.get_full_name,
            "user": user,
            "user_type": "student",
            "courses": courses,
            "student": student,
            "current_session": current_session,
            "current_semester": current_semester,
            "similar_users": similar_users,  # Pass similar users to the context
        }

        # Log in as the student
        login(request, student.student)

    else:
        context = {
            "title": user.get_full_name,
            "user": user,
            "user_type": "superuser",
            "current_session": current_session,
            "current_semester": current_semester,
            "similar_users": similar_users,  # Pass similar users to the context
        }
    return render(request, "accounts/profile_single.html", context)

@login_required
@admin_required
def admin_panel(request):
    return render(request, "setting/admin_panel.html", {})

# ########################################################
@login_required
def profile_update(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect("add_parent")
        else:
            messages.error(request, "Please correct the error(s) below.")
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(
        request,
        "setting/profile_info_change.html",
        {
            "title": "Setting | DjangoSMS",
            "form": form,
        },
    )

@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect("profile")
        else:
            messages.error(request, "Please correct the error(s) below. ")
    else:
        form = PasswordChangeForm(request.user)
    return render(
        request,
        "setting/password_change.html",
        {
            "form": form,
        },
    )


# ########################################################
@login_required
@admin_required
def staff_add_view(request):
    if request.method == "POST":
        form = StaffAddForm(request.POST)
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Account for lecturer "
                + first_name
                + " "
                + last_name
                + " has been created.",
            )
            return redirect("lecturer_list")
    else:
        form = StaffAddForm()

    context = {
        "title": "Lecturer Add | DjangoSMS",
        "form": form,
    }

    return render(request, "accounts/add_staff.html", context)


@login_required
@admin_required
def edit_staff(request, pk):
    instance = get_object_or_404(User, is_lecturer=True, pk=pk)
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=instance)
        full_name = instance.get_full_name
        if form.is_valid():
            form.save()

            messages.success(request, "Lecturer " + full_name + " has been updated.")
            return redirect("lecturer_list")
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = ProfileUpdateForm(instance=instance)
    return render(
        request,
        "accounts/edit_lecturer.html",
        {
            "title": "Edit Lecturer | DjangoSMS",
            "form": form,
        },
    )


@method_decorator([login_required, admin_required], name="dispatch")
class LecturerListView(ListView):
    model = User  # Use your User model
    template_name = "accounts/lecturer_list.html"
    paginate_by = 500  # Number of users per page
    context_object_name = 'lecturers'  # Update the context object name
    def get_queryset(self):
        queryset = User.objects.filter(is_lecturer=True)
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query) |
                Q(phone__icontains=query)
            )
        return queryset

# @login_required
# @lecturer_required
# def delete_staff(request, pk):
#     staff = get_object_or_404(User, pk=pk)
#     staff.delete()
#     return redirect('lecturer_list')

@login_required
@admin_required
def delete_staff(request, pk):
    lecturer = get_object_or_404(User, pk=pk)
    full_name = lecturer.get_full_name
    lecturer.delete()
    messages.success(request, "Lecturer " + full_name + " has been deleted.")
    return redirect("lecturer_list")

@login_required
@admin_required
def student_add_view(request):
    if request.method == "POST":
        form = StudentAddForm(request.POST)
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Account for " + first_name + " " + last_name + " has been created.",
            )
            return redirect("student_list")
        else:
            messages.error(request, "Correct the error(s) below.")
    else:
        form = StudentAddForm()
    return render(
        request,
        "accounts/add_student.html",
        {"title": "Add Student | DjangoSMS", "form": form},
    )


@login_required
@admin_required
def edit_student(request, pk):
    # instance = User.objects.get(pk=pk)
    instance = get_object_or_404(User, is_student=True, pk=pk)
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=instance)
        full_name = instance.get_full_name
        if form.is_valid():
            form.save()

            messages.success(request, ("Student " + full_name + " has been updated."))
            return redirect("student_list")
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = ProfileUpdateForm(instance=instance)
    return render(
        request,
        "accounts/edit_student.html",
        {
            "title": "Edit-profile | DjangoSMS",
            "form": form,
        },
    )

def schoolmate_view(request):
    return render(request, "accounts/schoolmate.html")

@method_decorator([login_required, admin_required], name="dispatch")
class StudentListView(View):
    model = Student
    template_name = "accounts/student_list.html"
    paginate_by = 3
    context_object_name = 'students'
    def get_queryset(self):
        queryset = Student.objects.all()
        query = self.request.GET.get("q")
        level = self.request.GET.get("level")
        session = self.request.GET.get("session")
        payment = self.request.GET.get("payment")

        if query:
            queryset = queryset.filter(
                Q(student__username__icontains=query) |
                Q(student__email__icontains=query) |
                Q(student__phone__icontains=query)
            )
        if level:
            queryset = queryset.filter(level=level)
        if session:
            queryset = queryset.filter(session=session)
        if payment:
            queryset = queryset.filter(payment=payment)
        return queryset

    def get(self, request):
        queryset = self.get_queryset()
        paginator = Paginator(queryset, self.paginate_by)
        page_number = request.GET.get("page")
        page = paginator.get_page(page_number)

        context = {
            "students": page,
            "filter_form": StudentFilterForm(self.request.GET),  # Include the filter form in the context
        }
        return render(request, self.template_name, context)

@login_required
@admin_required
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    # full_name = student.user.get_full_name
    student.delete()
    messages.success(request, "Student has been deleted.")
    return redirect("student_list")

def parentview(request):
    parent = Parent.objects.get(user=request.user)
    users_with_same_email = Parent.objects.filter(email_p=parent.email_p).exclude(user=request.user)
    return render(request, 'accounts/404.html', {'parent': parent, 'users_with_same_email': users_with_same_email})

@login_required
def ParentAdd(request):
    existing_parent = Parent.objects.filter(user=request.user).first()
    if existing_parent:
        messages.warning(request, 'You already have a parent associated with your account.')
        return redirect('profile')  # Redirect to the profile page

    relationship_options = [
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('uncle', 'Uncle'),
        ('aunt', 'Aunt'),
        ('brother', 'Brother'),
        ('sister', 'Sister'),
        ('step-mother', 'Step Mother'),
        ('step-father', 'Step Father'),
        ('Others', 'Other'),
    ]

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        occupation = request.POST.get('occupation')
        alt_phone = request.POST.get('alt_phone')
        relation_ship = request.POST.get('relation_ship')
        email_p = request.POST.get('email_p')
        save_obj = Parent(user=request.user, first_name=first_name, last_name=last_name,
                          occupation=occupation, alt_phone=alt_phone, relation_ship=relation_ship, email_p=email_p)
        save_obj.save()
        messages.success(request, 'Congratulations On Your Successful Registration')
        return redirect('assemble_payment')  # Redirect to the success page

    return render(request, 'accounts/parent_form.html', {'relationship_options': relationship_options})

# def parent_add(request):
#     if request.method == 'POST':
#         form = ParentAddForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('student_list')
#     else:
#         form = ParentAddForm(request.POST)


@login_required
def view_messages(request):
    student = request.user.student
    messages_based_on_filter = Message.objects.filter(
        department=student.department,
        level=student.level,
        year=student.session
    ).order_by('-created_at')
    messages_based_on_user_id = Message.objects.filter(students=request.user.student).order_by('-created_at')
    received_messages = messages_based_on_filter | messages_based_on_user_id
    unread_messages_count = Message.unread_count(
        student, student.level, student.session, student.department
    )
    return render(request, 'course/message.html', {
        'received_messages': received_messages,
        'unread_messages_count': unread_messages_count,
    })


@login_required
def open_message(request, message_id):
    student = request.user.student
    message = get_object_or_404(Message, pk=message_id)
    if message.students == request.user.student and not message.is_read:
        message.is_read = True
        message.save()

    unread_messages_count = Message.unread_count(
        student, student.level, student.session, student.department
    )

    return render(request, 'course/view_message.html', {
        'message': message,
        'unread_messages_count': unread_messages_count
    })
def assemble_payment(request):
    user_info = None
    if request.user.is_authenticated:
        user_info = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone': request.user.phone,
            'tx_ref': request.user.username,
            # Add more user attributes as needed
        }
    context = {
        "user_info": user_info,
    }
    return render(request, "accounts/payment_required.html", context)

class create_message(View):
    model = Student
    template_name = "accounts/message_form.html"
    paginate_by = 3
    context_object_name = 'students'
    def get_queryset(self):
        queryset = Student.objects.all()
        query = self.request.GET.get("q")
        level = self.request.GET.get("level")
        session = self.request.GET.get("session")
        payment = self.request.GET.get("payment")

        if query:
            queryset = queryset.filter(
                Q(student__username__icontains=query) |
                Q(student__email__icontains=query) |
                Q(student__phone__icontains=query)
            )
        if level:
            queryset = queryset.filter(level=level)
        if session:
            queryset = queryset.filter(session=session)
        if payment:
            queryset = queryset.filter(payment=payment)
        return queryset

    def get(self, request):
        queryset = self.get_queryset()
        paginator = Paginator(queryset, self.paginate_by)
        page_number = request.GET.get("page")
        page = paginator.get_page(page_number)

        context = {
            "students": page,
            "filter_form": StudentFilterForm(self.request.GET),  # Include the filter form in the context
            'form': MessageForm(),

        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = MessageForm(request.POST)
        if form.is_valid():
            # Process form data
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            selected_students = request.POST.getlist('selected_students')  # Retrieve selected student IDs from the form

            # Send messages to selected students
            for student_id in selected_students:
                student = Student.objects.get(id=student_id)  # Adjust this according to your model
                message = Message.objects.create(
                    title=title,
                    content=content,
                    students=student,  # Assign the selected student
                )
            messages.success(request, 'Message sent successfully to selected students.')
            return redirect('admin_panel')  # Redirect to a view displaying a list of students or a confirmation page

        # If form is not valid, render the form again with error messages
        context = {
            'form': form,
        }
        return render(request, self.template_name, context)
