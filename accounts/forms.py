from django import forms
from .models import CustomUser, Group

# Bootstrap stilini avtomatik qo‘shish uchun umumiy sinf
class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs.update({
                'class': 'form-control mb-3',
                'placeholder': visible.label
            })

# Ro‘yxatdan o‘tish formasi
class RegisterForm(BootstrapModelForm):
    password1 = forms.CharField(label="Parol", widget=forms.PasswordInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Parol'}))
    password2 = forms.CharField(label="Parolni tasdiqlang", widget=forms.PasswordInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Parolni tasdiqlang'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'first_name', 'last_name', 'profile_image']

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Parollar bir xil emas!")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

# O‘qituvchi formasi
class TeacherCreationForm(BootstrapModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'phone', 'first_name', 'last_name', 'profile_image']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'teacher'
        user.is_staff = True
        if commit:
            user.save()
        return user

# O‘quvchi formasi
class StudentCreationForm(BootstrapModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'phone', 'first_name', 'last_name', 'profile_image']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        if commit:
            user.save()
        return user

# Guruh formasi


from django import forms
from .models import Group, CustomUser
from django import forms
from .models import Group, CustomUser  # Importlar to‘g‘ri bo‘lishi kerak

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'teacher', 'lesson_start_time', 'lesson_end_time']  # ❌ 'students' olib tashlandi
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'teacher': forms.Select(attrs={'class': 'form-select mb-3'}),
            'lesson_start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control mb-3'}),
            'lesson_end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control mb-3'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # faqat teacherlarni chiqaramiz
        self.fields['teacher'].queryset = CustomUser.objects.filter(role='teacher')
# yangi guruhda hech kim tanlanmagan bo‘ladi




from django import forms
from .models import StudentGroup, CustomUser, Group

class StudentGroupForm(forms.ModelForm):
    class Meta:
        model = StudentGroup
        fields = ['student', 'group']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select mb-3'}),
            'group': forms.Select(attrs={'class': 'form-select mb-3'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = CustomUser.objects.filter(role='student')
from django import forms
from .models import Attendance  # yoki: from attendance.models import Attendance

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'group', 'date', 'status', 'score']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select mb-3'}),
            'group': forms.Select(attrs={'class': 'form-select mb-3'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control mb-3'}),
            'status': forms.Select(attrs={'class': 'form-select mb-3'}),
            'score': forms.NumberInput(attrs={'class': 'form-control mb-3'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = CustomUser.objects.filter(role='student')
from django import forms
from .models import Notification

class NotificationForm(forms.ModelForm):
    extra_message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Qo‘shimcha xabar (ixtiyoriy)'
        })
    )

    class Meta:
        model = Notification
        exclude = []


    def __init__(self, *args, **kwargs):
        student_instance = kwargs.pop('student_instance', None)
        super().__init__(*args, **kwargs)
        self.fields['student'].widget = forms.HiddenInput()
        if student_instance:
            self.fields['student'].initial = student_instance



