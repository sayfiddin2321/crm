# users/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from datetime import date, timedelta

from accounts.models import Group, Attendance, Notification
from coins.models import NanoCoinTransaction  # coinlar shu yerdan olinadi

# === Rollarni tekshiruvchi funksiyalar ===
def is_teacher(user):
    return user.is_authenticated and user.role == 'teacher'

def is_student(user):
    return user.is_authenticated and user.role == 'student'

# === O‘qituvchi bosh sahifasi ===
@login_required
@user_passes_test(is_teacher)
def teacher_index(request):
    teacher = request.user
    groups = Group.objects.filter(teacher=teacher)
    attendances = Attendance.objects.filter(group__in=groups)

    statistics = []
    for group in groups:
        group_attendance = Attendance.objects.filter(group=group)
        total = group_attendance.count()
        present = group_attendance.filter(status='present').count()
        percent = round((present / total * 100), 1) if total else 0
        avg_score = group_attendance.aggregate(Sum('score'))['score__sum'] or 0

        statistics.append({
            'group': group,
            'attendance_percent': percent,
            'avg_score': avg_score,
        })

    context = {
        'teacher': teacher,
        'groups': groups,
        'attendances': attendances,
        'statistics': statistics,
    }
    return render(request, 'accounts/teacher_index.html', context)

# === O‘quvchi bosh sahifasi (coinlar ko‘rinadi) ===
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from datetime import date, timedelta

from accounts.models import Group, Attendance, Notification, CustomUser
from coins.models import NanoCoinTransaction

# === Rollarni tekshiruvchi funksiyalar ===
def is_student(user):
    return user.is_authenticated and user.role == 'student'

# users/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from datetime import date, timedelta

from accounts.models import CustomUser, Group, Attendance, Notification
from coins.models import NanoCoinTransaction

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from datetime import date, timedelta

from accounts.models import Group, Notification
from accounts.models import Attendance
from coins.models import NanoCoinTransaction

# 👤 Faqat o‘quvchilar kirishi mumkin bo‘lgan decorator
def is_student(user):
    return user.is_authenticated and user.role == 'student'

# === O‘quvchi bosh sahifasi ===
from .models import StudentTest
from accounts.models import Test
import random

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import date, timedelta
from django.db.models import Sum
from coins.models import NanoCoinTransaction
from accounts.models import Test, Notification
from accounts.models import Attendance
from accounts.models import Group
from users.models import StudentTest
import random

def is_student(user):
    return user.is_authenticated and user.role == "student"
from django.db.models import Sum
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from datetime import date, timedelta
import random

from accounts.models import Group, Notification, Attendance, Test
from users.models import StudentTest
from coins.models import NanoCoinTransaction, CashTransaction

def is_student(user):
    return user.is_authenticated and user.role == "student"

@login_required
@user_passes_test(is_student)
def student_index(request):
    student = request.user
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    # 1️⃣ Guruh va o‘qituvchi
    student_group = (
        Group.objects.filter(students=student)
        .select_related('teacher')
        .first()
    )

    # 2️⃣ Bildirishnomalar
    notifications = Notification.objects.filter(student=student)

    # 3️⃣ Davomat statistikasi
    all_attendance = Attendance.objects.filter(student=student).order_by('-date')
    
    weekly_present = sum(1 for a in all_attendance if a.date >= week_start and a.status == 'present')
    weekly_total   = sum(1 for a in all_attendance if a.date >= week_start)

    monthly_present = sum(1 for a in all_attendance if a.date >= month_start and a.status == 'present')
    monthly_total   = sum(1 for a in all_attendance if a.date >= month_start)

    # 4️⃣ Coin transaction
    coin_tx = NanoCoinTransaction.objects.filter(student=student).order_by('-created_at')

    earned_total = (
        NanoCoinTransaction.objects.filter(student=student, amount__gt=0)
        .aggregate(total=Sum("amount"))['total'] or 0
    )
    cash_total = (
        CashTransaction.objects.filter(student=student, amount__gt=0)
        .aggregate(total=Sum("amount"))['total'] or 0
    )

    # 5️⃣ Testlar biriktirish
    assigned_tests = StudentTest.objects.filter(student=student)
    if not assigned_tests.exists():
        available_tests = list(Test.objects.all())
        random_tests = random.sample(available_tests, k=min(5, len(available_tests)))
        StudentTest.objects.bulk_create([
            StudentTest(student=student, test=test, is_active=True) for test in random_tests
        ])
        assigned_tests = StudentTest.objects.filter(student=student)

    active_tests = assigned_tests.filter(is_active=True)

    # 6️⃣ Test natijalari
    test_results = assigned_tests.filter(is_completed=True).order_by('-completed_at')

    # 7️⃣ Context
    context = {
        "student": student,
        "student_group": student_group,
        "notifications": notifications,
        "weekly_present": weekly_present,
        "weekly_total": weekly_total,
        "monthly_present": monthly_present,
        "monthly_total": monthly_total,
        "attendances": all_attendance,
        "coin_tx": coin_tx,
        "earned_total": earned_total,
        "cash_total": cash_total,
        "nanocoin": student.nanocoin,
        "cash_balance": student.cash_balance,
        "assigned_tests": active_tests,
        "test_results": test_results,
    }
    return render(request, "accounts/student_index.html", context)



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

def is_student(user):
    return user.is_authenticated and user.role == 'student'

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from coins.models import CashTransaction
@login_required
@user_passes_test(is_student)
def convert_coins(request):
    student = request.user
    if request.method == "POST":
        amount = int(request.POST.get("amount", 0))
        if amount <= 0:
            messages.error(request, "Miqdor 0 dan katta bo‘lishi kerak.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        if student.nanocoin < amount:
            messages.error(request, "Sizda yetarli coin yo‘q.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        cash_amount = amount * 1000  # 1 coin = 1000 so‘m
        student.nanocoin -= amount
        student.cash_balance += cash_amount
        student.save()

        # tranzaksiya yozamiz
        NanoCoinTransaction.objects.create(
            student=student,
            amount=-amount,
            reason=f"{amount} coin pulga almashtirildi"
        )
        CashTransaction.objects.create(
            student=student,
            amount=cash_amount,
            reason=f"{amount} coin almashtirish"
        )

        messages.success(request, f"✅ {amount} coin muvaffaqiyatli {cash_amount} so‘mga almashtirildi.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    return render(request, "coins/convert_coins.html", {
        "nanocoin": student.nanocoin,
        "cash_balance": student.cash_balance,
    })




from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from accounts.models import Test, Question, Answer
from users.models import StudentTest
from coins.models import NanoCoinTransaction  # tranzaksiyani yozish uchun

def is_student(user):
    return user.is_authenticated and user.role == "student"
@login_required
@user_passes_test(is_student)
def take_test(request, test_id):
    student = request.user
    test = get_object_or_404(Test, id=test_id)

    student_test = StudentTest.objects.filter(student=student, test=test, is_active=True).first()
    if not student_test:
        return render(request, "accounts/take_test.html", {"test": test})

    if student_test.is_completed:
        if student_test.score > 0:
            messages.warning(request, "Bu testni allaqachon to‘g‘ri ishlagansiz, qayta topshirolmaysiz.")
            return redirect("users:student_index")
        else:
            # qayta urinish uchun yana ochamiz
            student_test.is_active = True
            student_test.is_completed = False
            student_test.save()

    questions = Question.objects.filter(test=test).prefetch_related("answers")

    if request.method == "POST":
        correct_answers = 0
        total_questions = questions.count()

        for question in questions:
            selected_answer_id = request.POST.get(f"question_{question.id}")
            if selected_answer_id:
                is_correct = Answer.objects.filter(
                    id=selected_answer_id,
                    question=question,
                    is_correct=True
                ).exists()
                if is_correct:
                    correct_answers += 1

        score = int(correct_answers / total_questions * 100) if total_questions else 0
        earned_coins = score // 10

        student_test.is_completed = True
        student_test.is_active = False
        student_test.score = score
        student_test.earned_coins = earned_coins
        student_test.completed_at = timezone.now()
        student_test.save()

        if earned_coins > 0:
            student.nanocoin += earned_coins
            student.save()

            NanoCoinTransaction.objects.create(
                student=student,
                amount=earned_coins,
                reason=f"Test '{test.title}' uchun"
            )

        messages.success(
            request,
            f"✅ Test yakunlandi: {score}% ball, +{earned_coins} coin"
        )
        return redirect("users:student_index")

    context = {
        "test": test,
        "questions": questions,
    }
    return render(request, "accounts/take_test.html", context)

@login_required
@user_passes_test(is_student)
def refresh_tests(request):
    student = request.user

    # eski testlarni bloklaydi
    StudentTest.objects.filter(student=student, is_active=True).update(is_active=False)

    # ishlanmagan testlardan yangidan 30 ta tayinlash
    old_tests = StudentTest.objects.filter(student=student).values_list("test_id", flat=True)
    new_tests = Test.objects.exclude(id__in=old_tests).order_by("?")[:30]

    for test in new_tests:
        StudentTest.objects.create(student=student, test=test)

    messages.success(request, "Yangi 30 ta test tayinlandi!")
    return redirect("users:student_index")
@login_required
@user_passes_test(is_student)
def delete_all_tests(request):
    student = request.user
    StudentTest.objects.filter(student=student, is_active=True).update(is_active=False)
    messages.success(request, "Hamma testlaringiz o‘chirildi!")
    return redirect("users:student_index")
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import StudentTest

def delete_test_result(request, result_id):
    result = get_object_or_404(StudentTest, id=result_id, student=request.user)
    result.delete()
    messages.success(request, "Test natijasi muvaffaqiyatli o‘chirildi.")
    return redirect('users:student_index')   # kerak bo‘lsa student profiliga qaytarasiz
