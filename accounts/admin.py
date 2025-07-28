from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from openpyxl import Workbook
import csv
from datetime import timedelta
from django.utils import timezone

from .models import CustomUser, Group, Attendance, Banner, Test, Question, Answer
from .forms import RegisterForm

# ================== CustomUser PDF export ==================
def export_users_pdf(modeladmin, request, queryset):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="foydalanuvchilar.pdf"'
    p = canvas.Canvas(response, pagesize=letter)
    p.setFont("Helvetica", 12)
    p.drawString(100, 750, "Foydalanuvchilar ro‘yxati")
    y = 730
    for user in queryset:
        p.drawString(100, y, f"{user.first_name} {user.last_name} - {user.username}")
        y -= 20
        if y < 100:
            p.showPage()
            p.setFont("Helvetica", 12)
            y = 750
    p.save()
    return response
export_users_pdf.short_description = "Tanlangan foydalanuvchilarni PDFga eksport qilish"

# ================== CustomUser Excel export ==================
def export_users_excel(modeladmin, request, queryset):
    wb = Workbook()
    ws = wb.active
    ws.append(['Username', 'First name', 'Last name', 'Phone', 'Role', 'Is staff', 'Is active'])
    for user in queryset:
        ws.append([
            user.username,
            user.first_name,
            user.last_name,
            user.phone,
            user.role,
            user.is_staff,
            user.is_active
        ])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="foydalanuvchilar.xlsx"'
    wb.save(response)
    return response
export_users_excel.short_description = "Tanlangan foydalanuvchilarni EXCELga eksport qilish"

# ================== CustomUser CSV export ==================
def export_users_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="foydalanuvchilar.csv"'
    writer = csv.writer(response)
    writer.writerow(['Username', 'First name', 'Last name', 'Phone', 'Role', 'Is staff', 'Is active'])
    for user in queryset:
        writer.writerow([
            user.username,
            user.first_name,
            user.last_name,
            user.phone,
            user.role,
            user.is_staff,
            user.is_active
        ])
    return response
export_users_csv.short_description = "Tanlangan foydalanuvchilarni CSVga eksport qilish"

# ================== CustomUserAdmin ==================
class CustomUserAdmin(UserAdmin):
    add_form = RegisterForm
    model = CustomUser
    list_display = ('username', 'phone', 'first_name', 'last_name', 'role', 'telegram_chat_id', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'phone', 'first_name', 'last_name')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'phone', 'email', 'first_name', 'last_name', 'password', 'telegram_chat_id')}),
        ('Permissions', {'fields': ('role', 'is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Extra Info', {'fields': ('profile_image',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'phone', 'first_name', 'last_name', 'role', 'password1', 'password2', 'telegram_chat_id', 'is_staff', 'is_active')
        }),
    )
    actions = [export_users_pdf, export_users_excel, export_users_csv]

# ================== Group attendance PDF export ==================
def export_group_attendance_pdf(modeladmin, request, queryset):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="guruh_davomati.pdf"'
    p = canvas.Canvas(response, pagesize=letter)
    today = timezone.now().date()
    one_week_ago = today - timedelta(weeks=1)
    one_month_ago = today - timedelta(days=30)
    one_year_ago = today - timedelta(days=365)
    p.setFont("Helvetica", 12)

    for group in queryset:
        p.drawString(100, 750, f"Guruh: {group.name} Davomat Hisoboti")
        y = 720
        for student in group.students.all():
            weekly = Attendance.objects.filter(student=student, group=group, date__gte=one_week_ago)
            monthly = Attendance.objects.filter(student=student, group=group, date__gte=one_month_ago)
            yearly = Attendance.objects.filter(student=student, group=group, date__gte=one_year_ago)
            weekly_present = sum(1 for a in weekly if a.status == 'present')
            monthly_present = sum(1 for a in monthly if a.status == 'present')
            yearly_present = sum(1 for a in yearly if a.status == 'present')
            p.drawString(100, y, f"{student.first_name} {student.last_name} ({student.username})")
            y -= 20
            p.drawString(120, y, f"Haftalik: {weekly_present}/{weekly.count()}  Oylik: {monthly_present}/{monthly.count()}  Yillik: {yearly_present}/{yearly.count()}")
            y -= 30
            if y < 100:
                p.showPage()
                p.setFont("Helvetica", 12)
                p.drawString(100, 750, f"Guruh: {group.name} Davomat Hisoboti")
                y = 720
    p.save()
    return response
export_group_attendance_pdf.short_description = "Guruh davomatini PDFga eksport qilish"

# ================== Group attendance Excel export ==================
def export_group_attendance_excel(modeladmin, request, queryset):
    wb = Workbook()
    ws = wb.active
    ws.append(['Guruh', 'Student', 'Haftalik', 'Oylik', 'Yillik'])
    today = timezone.now().date()
    one_week_ago = today - timedelta(weeks=1)
    one_month_ago = today - timedelta(days=30)
    one_year_ago = today - timedelta(days=365)
    for group in queryset:
        for student in group.students.all():
            weekly = Attendance.objects.filter(student=student, group=group, date__gte=one_week_ago)
            monthly = Attendance.objects.filter(student=student, group=group, date__gte=one_month_ago)
            yearly = Attendance.objects.filter(student=student, group=group, date__gte=one_year_ago)
            weekly_present = sum(1 for a in weekly if a.status == 'present')
            monthly_present = sum(1 for a in monthly if a.status == 'present')
            yearly_present = sum(1 for a in yearly if a.status == 'present')
            ws.append([
                group.name,
                f"{student.first_name} {student.last_name}",
                f"{weekly_present}/{weekly.count()}",
                f"{monthly_present}/{monthly.count()}",
                f"{yearly_present}/{yearly.count()}"
            ])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="guruh_davomati.xlsx"'
    wb.save(response)
    return response
export_group_attendance_excel.short_description = "Guruh davomatini EXCELga eksport qilish"

# ================== Group attendance CSV export ==================
def export_group_attendance_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="guruh_davomati.csv"'
    writer = csv.writer(response)
    writer.writerow(['Guruh', 'Student', 'Haftalik', 'Oylik', 'Yillik'])
    today = timezone.now().date()
    one_week_ago = today - timedelta(weeks=1)
    one_month_ago = today - timedelta(days=30)
    one_year_ago = today - timedelta(days=365)
    for group in queryset:
        for student in group.students.all():
            weekly = Attendance.objects.filter(student=student, group=group, date__gte=one_week_ago)
            monthly = Attendance.objects.filter(student=student, group=group, date__gte=one_month_ago)
            yearly = Attendance.objects.filter(student=student, group=group, date__gte=one_year_ago)
            weekly_present = sum(1 for a in weekly if a.status == 'present')
            monthly_present = sum(1 for a in monthly if a.status == 'present')
            yearly_present = sum(1 for a in yearly if a.status == 'present')
            writer.writerow([
                group.name,
                f"{student.first_name} {student.last_name}",
                f"{weekly_present}/{weekly.count()}",
                f"{monthly_present}/{monthly.count()}",
                f"{yearly_present}/{yearly.count()}"
            ])
    return response
export_group_attendance_csv.short_description = "Guruh davomatini CSVga eksport qilish"

# ================== GroupAdmin ==================
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'created_at', 'lesson_start_time', 'lesson_end_time')
    search_fields = ('name', 'teacher__username')
    actions = [export_group_attendance_pdf, export_group_attendance_excel, export_group_attendance_csv]

# ================== Test / Question / Answer ==================
@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at')
    search_fields = ('title',)

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 2

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]

admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)

# ================== Register models ==================
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Attendance)
admin.site.register(Banner)
