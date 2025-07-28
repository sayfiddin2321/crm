from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import RegisterForm, TeacherCreationForm, GroupForm, StudentCreationForm
from .models import CustomUser, Group
from django.contrib.auth.decorators import login_required

User = get_user_model()
from datetime import timedelta
from django.utils import timezone
from accounts.models import Attendance
from django.contrib.auth.decorators import user_passes_test
from .models import AdmissionRequest
@login_required
@user_passes_test(lambda u: u.is_superuser)
def center_weekly_stats(request):
    today = timezone.now().date()
    start_date = today - timedelta(days=7)

    # Attendances ni olish
    attendances = Attendance.objects.filter(date__range=[start_date, today])

    total = attendances.count()
    present = attendances.filter(status='present').count()
    absent = attendances.filter(status='absent').count()

    # Prevent division by zero
    percent = (present / total * 100) if total else 0

    context = {
        'total': total,
        'present': present,
        'absent': absent,
        'percent': round(percent, 1),
        'start_date': start_date,
        'end_date': today,
    }
    return render(request, 'accounts/center_weekly_stats.html', context)


from .models import Banner # Banner modelini import qilamiz

@login_required
def Index(request):
    if request.user.role != 'admin':
        messages.warning(request, "Sizda bu sahifaga kirish huquqi yo‘q.")
        return redirect('accounts:login')

    banners = Banner.objects.filter(is_active=True)  # faqat faol bannerlar

    return render(request, 'accounts/index.html', {
        'banners': banners  # context orqali templatega uzatamiz
    })  
# Ro'yxatdan o'tish
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from accounts.models import CustomUser  # sizda qaysi model bo‘lsa
# yoki: from django.contrib.auth import get_user_model
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'student'  # Foydalanuvchi roli avtomatik 'student'
            user.save()
            messages.success(request, "Ro‘yxatdan o‘tdingiz. Endi tizimga kiring.")
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            # ✅ Rolga qarab yo‘naltirish
            if user.role == 'admin':
                return redirect('/accounts/index/')  # Admin uchun
            elif user.role == 'teacher':
                return redirect('/users/teacher/')   # O‘qituvchi uchun
            elif user.role == 'student':
                return redirect('/users/student/')   # O‘quvchi uchun
            else:
                messages.warning(request, "Roli aniqlanmadi.")
                return redirect('accounts:login')
        else:
            messages.error(request, "Username yoki parol noto'g'ri.")
    return render(request, 'accounts/login.html')

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Logout bo‘lib ketmasligi uchun
            messages.success(request, "Parol muvaffaqiyatli o‘zgartirildi!")
            return redirect('change_password')
        else:
            messages.error(request, "Iltimos, to‘g‘ri ma'lumot kiriting.")
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'accounts/change_password.html', {'form': form})


# Logout qilish
def logout_view(request):
    logout(request)
    return redirect('accounts:login')
    
# O'qituvchi qo‘shish
def add_teacher(request):
    if request.method == 'POST':
        form = TeacherCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts:teacher_list')
    else:
        form = TeacherCreationForm()
    return render(request, 'accounts/add_teacher.html', {'form': form})

# O‘quvchi qo‘shish
from accounts.models import AdmissionRequest  # modeli bo‘lishi kerak

def add_student(request):
    if request.method == 'POST':
        form = StudentCreationForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save(commit=False)
            student.role = 'student'
            student.save()

            # ⬇️ Student bilan birga qabul so‘rovi yaratiladi
            AdmissionRequest.objects.create(
                student=student,
                is_approved=False
            )

            return redirect('accounts:student_list')
    else:
        form = StudentCreationForm()

    return render(request, 'accounts/add_student.html', {'form': form})

from django.contrib.auth.decorators import login_required, user_passes_test

from .models import AdmissionRequest
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
@user_passes_test(lambda u: u.role == 'admin')
def admission_requests(request):
    requests = AdmissionRequest.objects.all()
    return render(request, 'accounts/admission_requests.html', {'requests': requests})
from django.shortcuts import get_object_or_404, redirect
from accounts.models import AdmissionRequest

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

@login_required
@user_passes_test(lambda u: u.role == 'admin')  # Faqat admin ruxsati bilan
def approve_admission(request, pk):
    admission = get_object_or_404(AdmissionRequest, pk=pk)
    admission.is_approved = True
    admission.save()
    messages.success(request, f"{admission.full_name} muvaffaqiyatli tasdiqlandi!")
    return redirect('accounts:admission_requests')  # qaytish uchun




def add_student_to_group(request):
    if request.method == 'POST':
        group_id = request.POST.get('group')
        student_id = request.POST.get('student')

        group = Group.objects.get(id=group_id)
        student = CustomUser.objects.get(id=student_id)

        # ✅ Qabuldan o'tganini tekshiramiz
        if hasattr(student, 'admission_request') and student.admission_request.is_approved:
            group.students.add(student)
            messages.success(request, f"{student.username} guruhga qo‘shildi.")
        else:
            messages.warning(request, f"{student.username} hali qabuldan o‘tmagan. Avval tasdiqlang.")

        return redirect('accounts:group_list')
    else:
        groups = Group.objects.all()
        students = CustomUser.objects.filter(
        role='student',
        admission_request__is_approved=True  # ✅ faqat tasdiqlanganlar
        )
        return render(request, 'accounts/add_student_to_group.html', {
        'groups': groups,
        'students': students
    })

# Guruh qo‘shish
from django.shortcuts import render, redirect
from .forms import GroupForm
def add_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts:group_list')
    else:
        form = GroupForm()

    return render(request, 'accounts/add_group.html', {'form': form})
from .forms import StudentGroupForm
# views.py

def add_student_to_group(request):
    if request.method == 'POST':
        group_id = request.POST.get('group')
        student_id = request.POST.get('student')

        group = Group.objects.get(id=group_id)
        student = CustomUser.objects.get(id=student_id)

        group.students.add(student)  # M:N aloqaga qo‘shiladi

        return redirect('accounts:group_list')  # bu all-groups url name bo‘lsa kerak
    else:
        groups = Group.objects.all()
        students = CustomUser.objects.filter(role='student')
        return render(request, 'accounts/add_student_to_group.html', {
            'groups': groups,
            'students': students
        })




# Ro'yxatlar
def teacher_list(request):
    teachers = CustomUser.objects.filter(role='teacher')
    return render(request, 'accounts/teacher_list.html', {'teachers': teachers})
# views.py
def teacher_detail(request, pk):
    teacher = get_object_or_404(CustomUser, pk=pk)
    groups = Group.objects.filter(teacher=teacher)
    return render(request, 'accounts/teacher_detail.html', {
        'teacher': teacher,
        'groups': groups
    })


from datetime import date, timedelta
from django.shortcuts import render
from .models import CustomUser, Attendance

from datetime import date, timedelta
from django.shortcuts import render
from accounts.models import CustomUser, Attendance
from django.db.models import Q

def student_list(request):
    # 🔍 Qidiruv so‘rovini olish
    search_query = request.GET.get('q', '').strip()

    # ✅ Faqat qabuldan o‘tgan studentlar
    students = CustomUser.objects.filter(
        role='student',
        admission_request__is_approved=True
    )

    # 🔍 Agar qidiruv bo‘lsa — filtrlash
    if search_query:
        students = students.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(username__icontains=search_query)
        )

    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    stats = {}
    for student in students:
        weekly_total = Attendance.objects.filter(student=student, date__gte=week_start).count()
        weekly_present = Attendance.objects.filter(student=student, date__gte=week_start, status='present').count()

        monthly_total = Attendance.objects.filter(student=student, date__gte=month_start).count()
        monthly_present = Attendance.objects.filter(student=student, date__gte=month_start, status='present').count()

        stats[student.id] = {
            'weekly_total': weekly_total,
            'weekly_present': weekly_present,
            'monthly_total': monthly_total,
            'monthly_present': monthly_present,
        }

    context = {
        'students': students,
        'stats': stats,
        'search_query': search_query  # 🔁 HTML formga qayta chiqarish uchun
    }

    return render(request, 'accounts/student_list.html', context)




from django.shortcuts import get_object_or_404, render, redirect
from .models import CustomUser, Attendance, Notification
from .forms import NotificationForm
from coins.forms import NanoCoinForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def student_detail(request, pk):
    student = get_object_or_404(CustomUser, pk=pk, role='student')
    attendances = Attendance.objects.filter(student=student).order_by('-date')
    present_count = attendances.filter(status='present').count()
    absent_count = attendances.filter(status='absent').count()
    scores = [a.score for a in attendances if a.score is not None]
    average_score = round(sum(scores) / len(scores), 1) if scores else None

    # === Notification form ===
    notification_form = NotificationForm(student_instance=student)
    if request.user.is_superuser or request.user.role == 'admin':
        if request.method == 'POST' and 'send_notification' in request.POST:
            notification_form = NotificationForm(request.POST, student_instance=student)
            if notification_form.is_valid():
                notification = notification_form.save(commit=False)
                # qo‘shimcha xabar biriktirish
                extra = notification_form.cleaned_data.get('extra_message')
                notification.message = request.POST.get('message', '')
                if extra:
                    notification.message += f"\n➕ {extra}"
                notification.student = student
                notification.save()
                messages.success(request, "✅ Bildirishnoma yuborildi.")
                return redirect('accounts:student_detail', pk=pk)

    # === NanoCoin form ===
    coin_form = NanoCoinForm()
    if request.user.is_superuser or request.user.role == 'admin':
        if request.method == 'POST' and 'give_coin' in request.POST:
            coin_form = NanoCoinForm(request.POST)
            if coin_form.is_valid():
                coin = coin_form.save(commit=False)
                coin.student = student
                coin.save()
                student.nanocoin += coin.amount
                student.save()
                messages.success(request, f"{coin.amount} NANOcoin muvaffaqiyatli berildi.")
                return redirect('accounts:student_detail', pk=pk)

    notifications = Notification.objects.filter(student=student).order_by('-created_at')

    context = {
        'student': student,
        'attendances': attendances,
        'present_count': present_count,
        'absent_count': absent_count,
        'average_score': average_score,
        'notification_form': notification_form,
        'coin_form': coin_form,
        'notifications': notifications,
    }

    return render(request, 'accounts/student_detail.html', context)





def group_list(request):
    groups = Group.objects.all()
    return render(request, 'accounts/group_list.html', {'groups': groups})

# O‘chirish
@login_required
def delete_item(request, model_type, item_id):
    if model_type == 'teacher':
        item = get_object_or_404(CustomUser, id=item_id, role='teacher')
        redirect_url = 'accounts:teacher_list'
    elif model_type == 'student':
        item = get_object_or_404(CustomUser, id=item_id, role='student')
        redirect_url = 'accounts:student_list'
    elif model_type == 'group':
        item = get_object_or_404(Group, id=item_id)
        redirect_url = 'accounts:group_list'
    else:
        messages.error(request, "Noto‘g‘ri model turi!")
        return redirect('accounts:index')

    item.delete()
    messages.success(request, "🗑 Ma'lumot o‘chirildi.")
    return redirect(redirect_url)


# Universal tahrirlash
def edit_item_role(request, role, pk):
    if role == 'teacher':
        user = get_object_or_404(CustomUser, pk=pk, role='teacher')
        form_class = TeacherCreationForm
        redirect_url = 'teacher_list'

    elif role == 'student':
        user = get_object_or_404(CustomUser, pk=pk, role='student')
        form_class = StudentCreationForm
        redirect_url = 'student_list'

    elif role == 'group':
        user = get_object_or_404(Group, pk=pk)
        form_class = GroupForm
        redirect_url = 'group_list'

    else:
        return redirect('home')

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=user)
        if form.is_valid():
            if role == 'group':
                obj = form.save(commit=False)
                obj.save()
                form.save_m2m()  # 🟢 ManyToManyField saqlash
            else:
                form.save()
            return redirect(redirect_url)
    else:
        form = form_class(instance=user)

    return render(request, 'accounts/edit_item.html', {
        'form': form,
        'role': role,
        'user_obj': user
    })
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Attendance, Group, CustomUser



from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Attendance, Group, CustomUser

def group_detail(request, pk):
    group = get_object_or_404(Group, pk=pk)
    students = CustomUser.objects.filter(student_groups__id=group.id, role='student')
    teacher = group.teacher
    today = timezone.now().date()

    # Bugungi kun uchun har bir talabaga tegishli davomat statusini olish
    attendance_data = {}
    for student in students:
        # Talabaning bugungi kun uchun davomat ma'lumotlarini olish
        attendance = Attendance.objects.filter(student=student, group=group, date=today).first()
        # Agar davomat mavjud bo'lsa, status va bahoni olish
        if attendance:
            attendance_data[student.id] = {
                'status': attendance.status,
                'score': attendance.score
            }
        else:
            # Agar davomat mavjud bo'lmasa, None qiymatlarini saqlash
            attendance_data[student.id] = {
                'status': None,
                'score': None
            }

    # POST so'rovi kelganda davomatni yangilash
    if request.method == 'POST':
        attendance_update_data = []

        # Har bir talaba uchun davomatni yangilash
        for student in students:
            is_present = request.POST.get(f'status_{student.id}') == 'on'
            score = request.POST.get(f'score_{student.id}')

            # Davomatni yangi obyekt sifatida tayyorlash
            attendance_update_data.append(Attendance(
                student=student,
                group=group,
                date=today,
                status='present' if is_present else 'absent',
                score=int(score) if score else None
            ))

        # Eski davomat yozuvlarini o'chirish (bulk delete)
        Attendance.objects.filter(group=group, date=today, student__in=students).delete()
        
        # Yangi davomat yozuvlarini kiritish (bulk create)
        Attendance.objects.bulk_create(attendance_update_data)

        # Yangi davomatlarni saqlagandan so'ng sahifani yangilash
        return redirect('accounts:group_detail', pk=group.pk)

    # Kontekstni tayyorlash
    context = {
        'group': group,
        'students': students,
        'teacher': teacher,
        'today': today,
        'attendance_data': attendance_data,  # Davomatni shablonga yuborish
    }

    # Shablonni render qilish
    return render(request, 'accounts/group_detail.html', context)





from django.shortcuts import render

from django.utils import timezone
from .models import Attendance
from .models import Group, CustomUser, Attendance

from django.shortcuts import render
from .models import Attendance

def attendance_list(request):
    records = Attendance.objects.select_related('student', 'group').order_by('-date')
    return render(request, 'accounts/attendance_list.html', {
        'attendance_records': records
    })
from django.shortcuts import render, get_object_or_404
from datetime import date, timedelta
from .models import Attendance
from accounts.models import Group

def group_attendance_stats(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    today = date.today()
    one_week_ago = today - timedelta(days=7)
    one_month_ago = today - timedelta(days=30)

    students = group.students.all()

    # 1ta query bilan barcha attendance ma'lumotlarni tortamiz
    attendance_qs = Attendance.objects.filter(
        group=group,
        student__in=students,
        date__gte=one_month_ago
    )

    stats = []

    for student in students:
        student_attendance = [a for a in attendance_qs if a.student_id == student.id]

        weekly_attendance = [
            a for a in student_attendance if a.date >= one_week_ago
        ]

        monthly_attendance = student_attendance

        weekly_present = sum(1 for a in weekly_attendance if a.status == 'present')
        monthly_present = sum(1 for a in monthly_attendance if a.status == 'present')

        stats.append({
            'student': student,
            'weekly_present': weekly_present,
            'weekly_total': len(weekly_attendance),
            'monthly_present': monthly_present,
            'monthly_total': len(monthly_attendance),
        })

    return render(request, 'accounts/group_attendance_stats.html', {
        'group': group,
        'stats': stats,
    })



from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from .forms import NotificationForm

def is_superadmin(user):
    return user.is_superuser or user.role == 'admin'

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.timezone import now
from django.utils.formats import date_format

from .forms import NotificationForm
from .models import Notification
from accounts.models import CustomUser

def is_superadmin(user):
    return user.is_superuser or user.role == 'admin'

@login_required
@user_passes_test(is_superadmin)
def send_notification_to_student(request, student_id):
    student = get_object_or_404(CustomUser, id=student_id, role='student')

    if request.method == 'POST':
        form = NotificationForm(request.POST, student_instance=student)
        if form.is_valid():
            notif = form.save(commit=False)
            notif.message = request.POST.get('message')
            extra = form.cleaned_data.get('extra_message')
            if extra:
                notif.message += f"\n➕ {extra}"
            notif.save()
            messages.success(request, "✅ Xabar muvaffaqiyatli yuborildi.")
            return redirect('accounts:send-notification-student', student_id=student.id)
    else:
        form = NotificationForm(student_instance=student)

    notifications = Notification.objects.filter(student=student).order_by('-created_at')

    return render(request, 'accounts/student_detail.html', {
    'form': form,
    'student': student,
    'notifications': notifications,
})


@login_required
@user_passes_test(is_superadmin)
def delete_notification(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    student_id = notification.student.id
    notification.delete()
    messages.success(request, "🗑 Xabar o‘chirildi.")
    return redirect('accounts:send-notification-student', student_id=student_id)

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Test, Question, Answer

def add_test(request):
    if request.method == 'POST':
        # Test nomi va izohini olish
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        if not title:
            messages.error(request, "Test nomini kiritish shart.")
            return redirect('add_test')
        
        test = Test.objects.create(title=title, description=description)
        
        # Dinamik kelgan savollar
        questions_data = request.POST.getlist('question_text')
        
        for q_index, question_text in enumerate(questions_data):
            question = Question.objects.create(test=test, text=question_text)
            
            # Har savolga tegishli javoblar
            answer_texts = request.POST.getlist(f'answers_{q_index}')
            answer_corrects = request.POST.getlist(f'correct_{q_index}')
            
            for a_index, answer_text in enumerate(answer_texts):
                is_correct = str(a_index) in answer_corrects
                Answer.objects.create(
                    question=question,
                    text=answer_text,
                    is_correct=is_correct
                )
        
        messages.success(request, "✅ Test va savollar muvaffaqiyatli qo‘shildi.")
        return redirect('accounts:add_test')
    
    return render(request, 'accounts/add_test.html')


