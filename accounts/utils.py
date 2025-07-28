from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from .models import Attendance
from datetime import timedelta

def generate_attendance_pdf(student, group, start_date, end_date, period='haftalik'):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    full_name = f"{student.first_name} {student.last_name}"
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, 800, f"📄 Davomat hisobot: {full_name} ({student.username})")
    p.setFont("Helvetica", 12)
    p.drawString(50, 780, f"Guruh: {group.name}")
    p.drawString(50, 760, f"Hisobot davri: {start_date} — {end_date} ({period})")

    # Ma'lumotlar
    attendances = Attendance.objects.filter(
        student=student,
        group=group,
        date__range=(start_date, end_date)
    ).order_by('date')

    y = 730
    present_count = 0
    total = attendances.count()

    for att in attendances:
        status_icon = "✅" if att.status == 'present' else "❌"
        if att.status == 'present':
            present_count += 1
        p.drawString(50, y, f"{att.date}: {status_icon} {att.get_status_display()}")
        y -= 20

    # Yakun
    p.drawString(50, y - 20, f"Jami: {total} kun — {present_count} ta keldi, {total - present_count} ta kelmadi.")
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
