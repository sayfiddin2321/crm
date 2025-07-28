from django.urls import path
from . import views 
from .views import take_test
from .views import *
app_name = 'users'  # to‘g‘ri, bu 'users' app uchun

urlpatterns = [
    path('teacher/', views.teacher_index, name='teacher_index'),
    path('student/', views.student_index, name='student_index'),
    path('take/<int:test_id>/', take_test, name='take_test'),
    path("refresh-tests/", refresh_tests, name="refresh_tests"),
    path("delete-tests/", delete_all_tests, name="delete_all_tests"),
    path('delete-test-result/<int:result_id>/', delete_test_result, name='delete_test_result'),
    
]
