from django.db import models
from accounts.models import CustomUser

class NanoCoinTransaction(models.Model):
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "student"}
    )
    amount = models.PositiveIntegerField()
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.amount} coin"

class CashTransaction(models.Model):
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "student"}
    )
    amount = models.PositiveIntegerField()  # so‘mda qancha berildi
    coin_used = models.PositiveIntegerField()  # qancha coin sarfladi
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.amount} so‘m (coins: {self.coin_used})"




