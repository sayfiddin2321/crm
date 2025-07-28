# accounts/models.py (yoki users/models.py)

from django.db import models
from accounts.models import CustomUser, Test

class StudentTest(models.Model):
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name="student_tests"
    )
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name="student_tests"
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    score = models.IntegerField(null=True, blank=True)
    earned_coins = models.IntegerField(null=True, blank=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)   # student o‘chirsa false bo‘ladi

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.test.title}"

