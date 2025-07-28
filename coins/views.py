from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django import forms
from coins.models import NanoCoinTransaction, CashTransaction

def is_student(user):
    return user.is_authenticated and user.role == "student"

class CoinToCashForm(forms.Form):
    amount = forms.IntegerField(
        min_value=1,
        label="Almashtirmoqchi bo‘lgan coin miqdori"
    )

@login_required
@user_passes_test(is_student)
def convert_coins(request):
    student = request.user

    if request.method == "POST":
        form = CoinToCashForm(request.POST)
        if form.is_valid():
            coins = form.cleaned_data["amount"]

            if student.nanocoin >= coins:
                cash_amount = coins * 1000  # 1 coin = 1000 so‘m

                # student nanocoin kamaytiriladi
                student.nanocoin -= coins

                # student cash_balance oshiriladi
                if hasattr(student, "cash_balance"):
                    student.cash_balance += cash_amount
                else:
                    # agar cash_balance bo‘lmasa qo‘shib yuboramiz
                    student.cash_balance = cash_amount

                student.save()

                # coin transaction yozamiz (minus qilingan)
                NanoCoinTransaction.objects.create(
    student=student,
    amount=coins,  # ijobiy yoz
    reason=f"{coins} coin pulga almashtirildi (balansdan ayirildi)"
)

                # cash transaction yozamiz
                CashTransaction.objects.create(
                    student=student,
                    amount=cash_amount,
                    coin_used=coins
                )

                messages.success(request, f"{coins} coin muvaffaqiyatli {cash_amount} so‘m ga aylantirildi.")
                return redirect("users:student_index")
            else:
                form.add_error("amount", "Sizda yetarli coin yo‘q.")
    else:
        form = CoinToCashForm()

    return render(request, "accounts/student_index.html", {
        "form": form,
        "nanocoin": student.nanocoin,
        "cash_balance": getattr(student, "cash_balance", 0),
    })



from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from django.contrib import messages

@login_required
@user_passes_test(lambda u: u.is_authenticated and u.role == "student")
def clear_history(request):
    student = request.user
    if request.method == "POST":
        NanoCoinTransaction.objects.filter(student=student).delete()
        CashTransaction.objects.filter(student=student).delete()
        messages.success(request, "Tarix tozalandi.")
    return redirect("users:student_index")
@login_required
@user_passes_test(is_student)
def reset_cash_balance(request):
    student = request.user
    student.cash_balance = 0
    student.save()
    messages.success(request, "Balansingiz muvaffaqiyatli 0 ga tushirildi.")
    return redirect('users:student_index')
