from django.urls import path
from . import views
from .views import teacher_list
from .views import delete_item
from .views import *
from .views import Index

app_name = "accounts"
urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('add-teacher/', views.add_teacher, name='add_teacher'),
    path('add-group/', views.add_group, name='add_group'),
    path('groups/', views.group_list, name='group_list'),
    path('attendance-list/', views.attendance_list, name='attendance_list'),
    path('group/<int:group_id>/attendance-stats/', views.group_attendance_stats, name='group_attendance_stats'),
    path('add-students/', views.add_student, name='add_student'),  # bu ham kerak
    path('teachers/', teacher_list, name='teacher_list'),
    path('teachers/<int:pk>/', views.teacher_detail, name='teacher_detail'), # o'qituvchi profili
    path('students/', views.student_list, name='student_list'),  # bu ham kerak
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('delete/<str:model_type>/<int:item_id>/', delete_item, name='delete_item'),
    path('edit/<str:role>/<int:pk>/', views.edit_item_role, name='edit_item_role'),
    path('groups/<int:pk>/', views.group_detail, name='group_detail'),
    path('add-student-to-group/', add_student_to_group, name='add_student_to_group'),
    path('index/', views.Index, name='index'), # Bosh sahifa
    path('change-password/', views.change_password, name='change_password'),
    path('send-notification/<int:student_id>/', views.send_notification_to_student, name='send-notification-student'),
    path('delete-notification/<int:pk>/', views.delete_notification, name='delete-notification'),
    path('stats/center-weekly/', views.center_weekly_stats, name='center_weekly_stats'),
    path('admission-requests/', views.admission_requests, name='admission_requests'),
    path('approve-admission/<int:pk>/', views.approve_admission, name='approve_admission'),
    path('add-test/', add_test, name='add_test')

    #path('groups/edit/<int:pk>/', edit_group, name='edit_group'),
    # model_type emas, role bo‘lishi kerak
    # path('teachers/edit/<int:pk>/', views.edit_teacher, name='edit_teacher'),  # 🔧 SHU QATOR
    # path('teachers/delete/<int:pk>/', views.delete_teacher, name='delete_teacher'),  # agar kerak bo‘lsa

]

# urls.py

