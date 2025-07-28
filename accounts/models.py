from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone

# Custom user manager
from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Username kiritilishi shart.")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username=None, password=None, **extra_fields):
        if username is None:
            raise ValueError("Superuser uchun username kiritilishi shart.")

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser uchun is_staff=True bo‘lishi kerak.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser uchun is_superuser=True bo‘lishi kerak.")

        return self.create_user(username=username, password=password, **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})


# accounts/models.py

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from .models import CustomUserManager  # o‘zingizning manageringiz

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'O‘qituvchi'),
        ('student', 'O‘quvchi'),
    )

    username = models.CharField(
        max_length=150,
        unique=True
    )
    email = models.EmailField(
        unique=True,
        null=True,
        blank=True
    )
    phone = models.CharField(
        max_length=15,
        unique=True
    )
    first_name = models.CharField(
        max_length=100
    )
    last_name = models.CharField(
        max_length=100
    )
    profile_image = models.ImageField(
        upload_to='media/',
        blank=True,
        null=True
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student'
    )
    is_active = models.BooleanField(
        default=True
    )
    is_staff = models.BooleanField(
        default=False
    )
    date_joined = models.DateTimeField(
        default=timezone.now
    )

    nanocoin = models.PositiveIntegerField(
        default=0,
        help_text="Student coin balansi"
    )
    cash_balance = models.PositiveIntegerField(
        default=0,
        help_text="Student pul balansi (so‘m)"
    )
    telegram_chat_id = models.BigIntegerField(
        null=True,
        blank=True
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.username} ({self.role})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name






# Guruh modeli
from django.db import models
from .models import CustomUser  # to'g'ri yo'l bo'yicha

class Group(models.Model):
    name = models.CharField(max_length=100)

    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'teacher'},
        related_name='teacher_groups'
    )

    students = models.ManyToManyField(
        CustomUser,
        blank=True,
        limit_choices_to={'role': 'student'},
        related_name='student_groups'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    lesson_start_time = models.TimeField(null=True, blank=True)
    lesson_end_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return self.name


# O‘quvchini guruhga qo‘shish tarixi
class StudentGroup(models.Model):
    student   = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'}
    )
    group     = models.ForeignKey(Group, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} → {self.group.name}"
from django.utils import timezone

from django.db import models
from django.utils import timezone
from accounts.models import CustomUser, Group  # Agar boshqa appda bo‘lsa

from django.db import models
from django.utils import timezone
from accounts.models import CustomUser, Group

class Attendance(models.Model):
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='attendances'
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)  # Yangi kirish sanasi uchun default qiymat

    STATUS_CHOICES = (
        ('present', 'Keldi'),
        ('absent', 'Kelmagan'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='absent')

    score = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'group', 'date')  # Bir xil talabalarga bir nechta sana uchun ruxsat bermaydi

    def __str__(self):
        return f"{self.student.username} - {self.group.name} - {self.date} - {self.get_status_display()}"

    def is_present(self):
        """
        O'quvchining davomatini tekshirish: Keldi yoki kelmagan.
        """
        return self.status == 'present'

    def mark_absent(self):
        """
        O'quvchini kelmagan deb belgilash
        """
        self.status = 'absent'
        self.save()

    def mark_present(self):
        """
        O'quvchini keldi deb belgilash
        """
        self.status = 'present'
        self.save()


from django.db import models
from django.conf import settings

class Notification(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # CustomUser ni dinamik bog‘lash
        on_delete=models.CASCADE,
        related_name='notifications',  # student.notifications orqali olish mumkin
        limit_choices_to={'role': 'student'}
    )
    message = models.TextField(verbose_name='Xabar matni')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqt')

    def __str__(self):
        return f"{self.student.username} - {self.message[:30]}..."

class AdmissionRequest(models.Model):
    student = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='admission_request'
    )
    full_name = models.CharField(max_length=255)
    requested_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.username} ({'Tasdiqlandi' if self.is_approved else 'Kutilmoqda'})"

# models.py

class Banner(models.Model):
    title = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='banners/')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title or "Banner"
from django.db import models

class Test(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
class Question(models.Model):
    test = models.ForeignKey('Test', on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)

    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'to‘g‘ri' if self.is_correct else 'xato'})"
