from course.models import Program
from django.db import models
from django.urls import reverse
from django.conf import settings
import random
from datetime import datetime
from django.db.models import Q
from PIL import Image
from django.utils import timezone
from .validators import ASCIIUsernameValidator
from django.contrib.auth.models import AbstractUser, UserManager



FATHER = "Father"
MOTHER = "Mother"
BROTHER = "Brother"
SISTER = "Sister"
GRAND_MOTHER = "Grand mother"
GRAND_FATHER = "Grand father"
OTHER = "Other"

RELATION_SHIP  = (
    (FATHER, "Father"),
    (MOTHER, "Mother"),
    (BROTHER, "Brother"),
    (SISTER, "Sister"),
    (GRAND_MOTHER, "Grand mother"),
    (GRAND_FATHER, "Grand father"),
    (OTHER, "Other"),
)


BUS_SERVICE_CHOICES = [
    ('yes', 'Yes'),
    ('no', 'No'),
    ('not_now', 'Not Now'),
]

BUS_SERVICE_TYPE_CHOICES = [
    ('both-ways', 'Both Ways'),
    ('one-way', 'One-way'),
    ('not_now', 'Not Now'),

]

PICKUP_OR_DROPOFF_CHOICES = [
    ('pickup', 'Pickup'),
    ('dropoff', 'Dropoff'),
    ('not_now', 'Not Now'),

]

CHOICES = [
    ('yes', 'Yes'),
    ('no', 'No'),
    ('not_now', 'Not Now'),
]

ONE ='ONE'
TWO = 'TWO'
THREE ='THREE'
FOUR ='FOUR'
FIVE ='FIVE'
SIX ='SIX'

YEARS = (
        ('', '--'),  # Add an empty choice with "--" as value and label
        (ONE, 'ONE'),
        (TWO, 'TWO'),
        (THREE, 'THREE'),
        (FOUR, 'FOUR'),
        (FIVE, 'FIVE'),
        (SIX, 'SIX'),
    )

FIRST = "First"
SECOND = "Second"
THIRD = "Third"

SEMESTER = (
    ('', '--'),  # Add an empty choice with "--" as value and label
    (FIRST, "First"),
    (SECOND, "Second"),
    (THIRD, "Third"),
)

# LEVEL_COURSE = "Level course"
CREECH = "Creech"
NURSERY = "Nusery"
BASIC = "Basic"

LEVEL = (
    ('', '--'),  # Add an empty choice with "--" as value and label
    (CREECH, "Creech"),
    (NURSERY, "Nusery Certificate"),
    (BASIC,  "Basic Certificate")
)

PAYMENT_CHOICES = (
    ('', '--'),  # Add an empty choice with "--" as value and label
    ('PENDING  ❌', 'Pending'),
    ('APPROVED ✔', 'Approved'),
    ('ADVANCED 🕛', 'Advanced'),
)


class UserManager(UserManager):
    def search(self, query=None):
        qs = self.get_queryset()
        if query is not None:
            or_lookup = (Q(username__icontains=query) |
                         Q(first_name__icontains=query)|
                         Q(last_name__icontains=query)|
                         Q(email__icontains=query)
                        )
            qs = qs.filter(or_lookup).distinct() # distinct() is often necessary with Q lookups
        return qs


class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_lecturer = models.BooleanField(default=False)
    is_parent = models.BooleanField(default=False)
    is_dep_head = models.BooleanField(default=False)
    phone = models.CharField(max_length=60, blank=True, null=True)
    nationality = models.CharField(max_length=60, blank=True, null=True)
    address = models.CharField(max_length=60, blank=True, null=True)
    picture = models.ImageField(upload_to='profile_pictures/%y/%m/%d/', default='default.png', null=True)
    email = models.EmailField(blank=True, null=True)
    state_of_origin = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    meal_allergic_comment = models.TextField(blank=True, null=True)
    medical_record = models.FileField(upload_to='medical_records/', blank=True, null=True)
    computer_labs = models.CharField(max_length=10, choices=CHOICES, default='not_now')
    library_services = models.CharField(max_length=10, choices=CHOICES, default='not_now')
    counseling = models.CharField(max_length=10, choices=CHOICES, default='not_now')
    student_housing = models.CharField(max_length=10, choices=CHOICES, default='not_now')
    financial_aid = models.CharField(max_length=10, choices=CHOICES, default='not_now')
    cafeteria_services = models.CharField(max_length=10, choices=CHOICES, default='not_now')
    mental_health_services = models.CharField(max_length=10, choices=CHOICES, default='not_now')
    tutoring_centers = models.CharField(max_length=10, choices=CHOICES, default='not_now')
    technology_support = models.CharField(max_length=10, choices=CHOICES, default='not_now')
    disability_services = models.CharField(max_length=10, choices=CHOICES, default='not_now')
    international_student_services = models.CharField(max_length=10, choices=CHOICES, default='not_now')
    laboratory_facilities = models.CharField(max_length=10, choices=CHOICES, default='not_now')
    academic_advising = models.CharField(max_length=10, choices=CHOICES, default='not_now')
    bus_service = models.CharField(max_length=10, choices=BUS_SERVICE_CHOICES, default='not_now')
    bus_service_type = models.CharField(max_length=10, choices=BUS_SERVICE_TYPE_CHOICES, blank=True, null=True,default='not_now')
    pickup_or_dropoff = models.CharField(max_length=10, choices=PICKUP_OR_DROPOFF_CHOICES, blank=True, null=True,default='not_now')
    username_validator = ASCIIUsernameValidator()

    objects = UserManager()

    @property
    def get_full_name(self):
        full_name = self.username
        if self.first_name and self.last_name:
            full_name = self.first_name + " " + self.last_name
        return full_name

    def __str__(self):
        return '{} ({})'.format(self.username, self.get_full_name)

    @property
    def get_user_role(self):
        if self.is_superuser:
            return "Admin"
        elif self.is_student:
            return "Student"
        elif self.is_lecturer:
            return "Lecturer"
        elif self.is_parent:
            return "Parent"

    def get_picture(self):
        try:
            return self.picture.url
        except:
            no_picture = settings.MEDIA_URL + 'default.png'
            return no_picture

    def get_absolute_url(self):
        return reverse('profile_single', kwargs={'id': self.id})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            img = Image.open(self.picture.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.picture.path)
        except:
            pass

    def delete(self, *args, **kwargs):
        if self.picture.url != settings.MEDIA_URL + 'default.png':
            self.picture.delete()
        super().delete(*args, **kwargs)

class StudentManager(models.Manager):
    def search(self, query=None):
        qs = self.get_queryset()
        if query is not None:
            or_lookup = (Q(level__icontains=query) |
                         Q(department__icontains=query) |
                         Q(session__icontains=query))
            qs = qs.filter(or_lookup).distinct()
        return qs


class Student(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE, default='')
    Admission_id = models.CharField(max_length=20,  blank=True,default='')
    level = models.CharField(max_length=25, choices=LEVEL, default='')
    term = models.CharField(max_length=25, choices=SEMESTER,default='')
    session = models.CharField(max_length=25, choices=YEARS,default='')
    department = models.ForeignKey(Program, on_delete=models.CASCADE, null=True)
    payment = models.CharField(max_length=25, choices=PAYMENT_CHOICES, blank=True,null=True,default='')

    objects = StudentManager()

    def __str__(self):
        return f"{self.student}"

    def get_absolute_url(self):
        return reverse('profile_single', kwargs={'id': self.id})

    def delete(self, *args, **kwargs):
        self.student.delete()
        super().delete(*args, **kwargs)

    def generate_unique_admission_number(self):
        while True:
            random_number = random.randint(10000, 99999)
            current_year = datetime.now().year
            admission_number = f"HIGS/{random_number}/{current_year}"
            if not Student.objects.filter(Admission_id=admission_number).exists():
                return admission_number

    def save(self, *args, **kwargs):
        if not self.Admission_id:
            self.Admission_id = self.generate_unique_admission_number()
        super().save(*args, **kwargs)


class Message(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    students = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True, null=True)
    level = models.CharField(max_length=25, choices=LEVEL, default='', blank=True, null=True)
    year = models.CharField(max_length=25, choices=YEARS, default='', blank=True, null=True)
    department = models.ForeignKey(Program, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)


    @classmethod
    def unread_count(cls, Student, LEVEL, YEARS, program ):
        return cls.objects.filter(students=Student, level=LEVEL, year=YEARS, department=program, is_read=False).count()

    def __str__(self):
        return f"{self.title} read by {self.students} is {self.is_read}"


class Parent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    occupation = models.CharField(max_length=60, blank=True, null=True)
    alt_phone = models.CharField(max_length=60, blank=True, null=True)
    relation_ship = models.CharField(max_length=60, blank=True, null=True)
    email_p = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s {self.__class__.__name__}"

class DepartmentHead(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Program, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return "{}".format(self.user)

