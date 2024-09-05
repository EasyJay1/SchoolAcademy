from django import forms
from django.db import transaction
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm, PasswordResetForm
from course.models import Program
from .models import *


class StaffAddForm(UserCreationForm):
    username = forms.CharField(
        max_length=30, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', }),
        label="Username", )

    first_name = forms.CharField(
        max_length=30, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', }),
        label="First Name", )

    last_name = forms.CharField(
        max_length=30, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', }),
        label="Last Name", )

    phone = forms.CharField(
        max_length=30, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', }),
        label="Mobile No.", )

    email = forms.CharField(
        max_length=30, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', }),
        label="Email", )

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic()
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_lecturer = True
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.phone = self.cleaned_data.get('phone')
        user.address = self.cleaned_data.get('address')
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
        return user


class StudentAddForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
                'id': 'username_id',
                'placeholder': 'Create Username'
            }
        ),
        label="USERNAME",
    )
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                'type': 'email',
                'class': 'form-control',
                'id': 'email_id',
                'placeholder': 'Email Address'
            }
        ),
        label="Email",
    )
    phone = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'Number', 'class': 'form-control'}),
        label="Phone No.",
    )


    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
            }
        ),
        label="Child's First name",
    )

    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
            }
        ),
        label="Child's Last name",
    )

    level = forms.CharField(
        widget=forms.Select(
            choices=LEVEL,
            attrs={
                'class': 'browser-default custom-select form-control',
            }
        ),
    )

    department = forms.ModelChoiceField(
        queryset=Program.objects.all(),
        widget=forms.Select(attrs={'class': 'browser-default custom-select form-control'}),
        label="Programs",
    )
    session = forms.CharField(
        widget=forms.Select(
            choices=YEARS,
            attrs={
                'class': 'browser-default custom-select form-control',
            }
        ),
    )


    password1 = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'type': 'password', 'class': 'form-control', }),
        label="Password",
    )

    password2 = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'type': 'password', 'class': 'form-control', }),
        label="Password Confirmation",
    )

    accept_terms = forms.BooleanField(label='I accept the Terms and Conditions', required=True)

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic()
    def save(self):
        user = super().save(commit=False)
        user.is_student = True
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        user.phone = self.cleaned_data.get('phone')

        user.save()
        student = Student.objects.create(
            student=user,
            level=self.cleaned_data.get('level'),
            department=self.cleaned_data.get('department'),
            session=self.cleaned_data.get('session')
        )
        student.save()
        return user


from django import forms
from .models import Student
from django.contrib.auth.forms import UserChangeForm

class ProfileUpdateForm(UserChangeForm):
    picture = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control-file'}),
        label="Profile Picture",
        required=False,  # Set to True if the picture is required
    )

    address = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control'}),
        label="Address / city",
    )

    nationality = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control'}),
        label="Nationality",
    )

    state_of_origin = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control'}),
        label="State of Origin",
    )

    date_of_birth = forms.DateField(
        widget=forms.TextInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Date of Birth",
    )

    weight = forms.IntegerField(
        widget=forms.TextInput(attrs={'type': 'number', 'class': 'form-control'}),
        label="Weight",
    )

    height = forms.IntegerField(
        widget=forms.TextInput(attrs={'type': 'number', 'class': 'form-control'}),
        label="Height",
    )

    meal_allergic_comment = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'placeholder': 'Meal Allergic Comment',
                'rows': 3,  # Adjust the number of rows as needed
            }
        ),
        label="Meal Allergic Comment",
        required=False  # This field is optional
    )

    medical_record = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        label="Medical Record",
        required=False  # This field is optional
    )

    computer_labs = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Computer Labs",
        initial='not_now',  # Set the default value to 'Not Now'
        required=False,
    )

    library_services = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Library Services",
        initial='not_now',  # Set the default value to 'Not Now'
        required=False,
    )

    counseling = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Counseling",
        initial='not_now',  # Set the default value to 'Not Now'
        required=False,
    )

    student_housing = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='not_now',  # Set the default value to 'Not Now'
        required=False,
        label="Student Housing",
    )

    financial_aid = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='not_now',  # Set the default value to 'Not Now'
        required=False,
        label="Financial Aid",
    )

    cafeteria_services = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='not_now',  # Set the default value to 'Not Now'
        required=False,
        label="Cafeteria and Dining Services",
    )

    mental_health_services = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='not_now',  # Set the default value to 'Not Now'
        required=False,
        label="Counseling and Mental Health Services",
    )

    tutoring_centers = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='not_now',  # Set the default value to 'Not Now'
        required=False,
        label="Tutoring Centers",
    )

    technology_support = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='not_now',  # Set the default value to 'Not Now'
        required=False,
        label="Technology Support",
    )

    disability_services = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='not_now',  # Set the default value to 'Not Now'
        required=False,
        label="Disability Services",
    )

    international_student_services = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='not_now',  # Set the default value to 'Not Now'
        required=False,
        label="International Student Services",
    )
    laboratory_facilities = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='not_now',  # Set the default value to 'Not Now'
        label="Laboratory Facilities",
        required=False,
    )

    academic_advising = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='not_now',  # Set the default value to 'Not Now'
        label="Academic Advising",
        required=False,
    )

    bus_service = forms.ChoiceField(
        choices=BUS_SERVICE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Bus Service',
        initial='not_now',  # Set the default value to 'Not Now'
    )

    bus_service_type = forms.ChoiceField(
        choices=BUS_SERVICE_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Bus Service Type',
        required=False,  # Make it optional
        initial='',  # Set the default value to 'Not Now'

    )

    pickup_or_dropoff = forms.ChoiceField(
        choices=PICKUP_OR_DROPOFF_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Pickup or Dropoff',
        required=False,  # Make it optional
        initial='',  # Set the default value to 'Not Now'
    )

    class Meta:
        model = User
        fields = ['address', 'nationality', 'state_of_origin', 'date_of_birth', 'weight',
                  'height', 'meal_allergic_comment', 'medical_record', 'picture',
                  'library_services', 'computer_labs', 'laboratory_facilities', 'academic_advising', 'counseling',
                  'student_housing', 'financial_aid', 'cafeteria_services', 'mental_health_services',
                  'tutoring_centers', 'technology_support',  'disability_services',
                  'international_student_services','bus_service','bus_service_type','pickup_or_dropoff',]

class StudentFilterForm(forms.Form):
    level = forms.ChoiceField(choices=LEVEL, label='Level', required=False,)
    session = forms.ChoiceField(choices=YEARS, label='Session', required=False)
    payment = forms.ChoiceField(choices=PAYMENT_CHOICES,  label='Payment', required=False)


class ChatForm(forms.Form):
    message = forms.CharField(widget=forms.TextInput(attrs={'class': 'user-input'}))


class ParentAddForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
            }
        ),
        label="Username",
    )
    address = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
            }
        ),
        label="Address",
    )

    phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
            }
        ),
        label="Mobile No.",
    )

    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
            }
        ),
        label="First name",
    )

    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
            }
        ),
        label="Last name",
    )

    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                'type': 'email',
                'class': 'form-control',
            }
        ),
        label="Email Address",
    )

    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=forms.Select(attrs={'class': 'browser-default custom-select form-control'}),
        label="Student",
    )

    relation_ship = forms.CharField(
        widget=forms.Select(
            choices=RELATION_SHIP,
            attrs={'class': 'browser-default custom-select form-control',}
        ),
    )

    password1 = forms.CharField(
        max_length=30, widget=forms.TextInput(attrs={'type': 'password', 'class': 'form-control', }),
        label="Password", )

    password2 = forms.CharField(
        max_length=30, widget=forms.TextInput(attrs={'type': 'password', 'class': 'form-control', }),
        label="Password Confirmation", )

    # def validate_email(self):
    #     email = self.cleaned_data['email']
    #     if User.objects.filter(email__iexact=email, is_active=True).exists():
    #         raise forms.ValidationError("Email has taken, try another email address. ")

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic()
    def save(self):
        user = super().save(commit=False)
        user.is_parent = True
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.address = self.cleaned_data.get('address')
        user.phone = self.cleaned_data.get('phone')
        user.email = self.cleaned_data.get('email')
        user.save()
        parent = Parent.objects.create(
            user=user,
            student=self.cleaned_data.get('student'),
            relation_ship=self.cleaned_data.get('relation_ship')
        )
        parent.save()
        return user


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['students','title', 'content']  # Add other fields as needed


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label='Email', max_length=254,
                             widget=forms.EmailInput(attrs={'autocomplete': 'email'}))


class EmailValidationOnForgotPassword(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data.get('email')  # Use get() method to avoid KeyError
        if email:
            if not User.objects.filter(email__iexact=email, is_active=True).exists():
                msg = "There is no user registered with the specified E-mail address."
                self.add_error('email', msg)
        return email