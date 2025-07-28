from django.core.management.base import BaseCommand
from accounts.models import CustomUser, Group, StudentGroup, Attendance
from accounts.utils import generate_attendance_pdf
from datetime import date, timedelta
import os

class Command(BaseCommand):
    help = "Har haftalik davomat hisobotlarini PDF shaklida yaratadi"

    def handle(self, *args, **options):
        today = date.today()
        start_date = today - timedelta(days=7)  # Haftaning boshlanishi

        # Hisobotlarni saqlash uchun papka yaratish
        reports_dir = 'media/reports/weekly/'
        os.makedirs(reports_dir, exist_ok=True)

        # O'quvchilarni olish
        students = CustomUser.objects.filter(role='student')

        for student in students:
            # StudentGroup orqali guruhlarni olish
            student_groups = StudentGroup.objects.filter(student=student)
            for student_group in student_groups:
                group = student_group.group  # StudentGroup modelidan guruhni olish
                try:
                    buffer = generate_attendance_pdf(student, group, start_date, today, period='haftalik')
                    filename = f"davomat_haftalik_{student.username}_{group.name.replace(' ', '_')}.pdf"
                    file_path = os.path.join(reports_dir, filename)

                    with open(file_path, 'wb') as f:
                        f.write(buffer.read())
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ {student.username} uchun xatolik: {str(e)}"))

        self.stdout.write(self.style.SUCCESS("✅ Haftalik davomat hisobotlari yaratildi."))
