
from django.http import JsonResponse
from django.shortcuts import redirect, render
import pytz
import requests
from accounts.models import User
from exams.models import ExamDate, ExamQuestion, ExamRes, ExamStu
from project.views import send_by_bot, to_hijri
from tracks.models import Stage
from .models import Notes, Student
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import re

from .forms import BookDate, EditProfile, ExcuseForm
from django.utils import timezone
from datetime import date , datetime
from django.contrib import messages


today = date.today()




def count_progress(track, nsap):
    if track and nsap:
        if track == 'track_1':
            return round((nsap / 604) * 100, 2)
        elif track == 'track_2':
            return round((nsap/403)*100, 2)
        elif track == 'track_3':
            return round((nsap/201)*100, 2)
        else:
            return 0
    else:
        return 0


def arabic_plural(n, singular, dual, plural, feminine=False):
    if n == 0:
        return ''
    elif n == 1:
        return f"{singular} {'واحدة' if feminine else 'واحد'}"
    elif n == 2:
        return dual
    elif 3 <= n <= 10:
        return f"{n} {plural}"
    else:
        return f"{n} {singular}"

def sec_date(sec):
    if sec:
        days = sec // (24 * 60 * 60)
        remain = sec % (24 * 60 * 60)
        hours = remain // (60 * 60)
        remain %= (60 * 60)
        minutes = remain // 60

        parts = []
        if days:
            parts.append(arabic_plural(int(days), "يوم", "يومان", "أيام"))
        if hours:
            parts.append(arabic_plural(int(hours), "ساعة", "ساعتان", "ساعات", feminine=True))
        if minutes:
            parts.append(arabic_plural(int(minutes), "دقيقة", "دقيقتان", "دقائق", feminine=True))

        return "المتبقي: " + " و ".join(parts) if parts else "لا يوجد وقت متبقٍ"
    else:
        return 0




@login_required
def student_dash(request):
    role = request.user.role
    if role == 'student':
        student = Student.objects.filter(user=request.user).first()
        notes = Notes.objects.filter(user=student).all().order_by("-created_at")
        is_booking = ExamStu.objects.filter(student=student, date__tarkh__gt=today).exists()
        progress = count_progress(student.track.name, student.nsap)
        
        if request.method == 'POST':
            book_form = BookDate(request.POST)
            if book_form.is_valid():
                current_stage = Stage.objects.filter(is_active=True, track__batch= student.track.batch).last()
                save_user_date = book_form.save(commit=False)
                save_user_date.stage = current_stage
                save_user_date.student = student
                save_user_date.save()
                Student.objects.filter(user=request.user).update(nsap=book_form.cleaned_data['nsap'])
                messages.success(request, "تم الحجز في الموعد بحمد الله")
                hijri_date = to_hijri(save_user_date.date.tarkh)
                try:
                    send_by_bot(student.user.teleid, f'''
حياك الله {student.user.name}

تم حجز موعدكم يوم {hijri_date} بحمد الله

وفقكم الله وبارك فيكم
                            ''')
                except:
                    pass
                
                try:
                    send_by_bot(student.sheikh.user.teleid, f'''
حياك الله شيخ {student.sheikh.user.name}

 حجز الطالب @{student.user.tele} في موعدكم يوم {hijri_date}

وفقكم الله وأعانكم وبارك فيكم
                            ''')
                except:
                    pass
                
            return redirect("/dash")

        else:
            is_sheikh = student.sheikh
            if is_sheikh:
                dates = ExamDate.objects.filter(tarkh__gt=today, sheikh= is_sheikh)
            else:
                dates = ExamDate.objects.filter(tarkh__gt=today, sheikh__user__gender= student.user.gender, sheikh__rwia= student.rwia)
                
            available_dates = []

            for date in dates:
                booked = ExamStu.objects.filter(date=date).values('student').distinct().count()
                if booked < date.student_num:
                    available_dates.append(date)

            book_form = BookDate()
            book_form.fields['date'].queryset = ExamDate.objects.filter(id__in=[d.id for d in available_dates])


        next_exam = None 
        sec = 0
        try:
            next_exam_obj = ExamStu.objects.filter(student=student, date__tarkh__gt=today).order_by('date__tarkh').first()
        
                
            if next_exam_obj:
                date_booking = next_exam_obj.date.tarkh
                time_booking = next_exam_obj.date.from_hour
                next_exam_str = f"{date_booking} {time_booking}"
                next_exam_naive = datetime.strptime(next_exam_str, "%Y-%m-%d %H:%M:%S")
                riyadh_tz = pytz.timezone('Asia/Riyadh')
                next_exam = riyadh_tz.localize(next_exam_naive)
                now_in_riyadh = timezone.now().astimezone(riyadh_tz)
                remain = next_exam - now_in_riyadh
                sec = remain.total_seconds()
                if next_exam:
                    next_exam_by_hijri = to_hijri(next_exam)
        except: 
            next_exam_obj = "لا يوجد"
            next_exam_by_hijri = "لا يوجد"
        
        try:
            last_exam = ExamRes.objects.filter(student=student).last()
        except:
            last_exam = None
        
        for note in notes:
            note.hijri_created_at = to_hijri(note.created_at)
        context = {
            'notes': notes,
            'progress': progress,
            'next_exam_by_hijri': next_exam_by_hijri if next_exam else 'لم تحجز بعد',
            'last_score': round(((last_exam.score / 20) *100), 2) if last_exam else 0,
            'nsap': student.nsap if student.nsap else 0,
            'book_form': book_form,
            'is_booking': is_booking,
            'student': student,
            'next_exam_obj': next_exam_obj,
            'remain_time': sec_date(sec),
 
        }
        
        return render(request, 'students/html/student_dash.html', context)
    else:
        return redirect("/dash")

@require_POST
@login_required
def mark_notification_read(request, note_id):
    try:
        student = Student.objects.filter(user = request.user).first()
        note = Notes.objects.get(id=note_id, user=student)
        note.is_read = True  # غير اسم الحقل حسب اللي عندك
        note.save()
        return JsonResponse({'success': True})
    except Notes.DoesNotExist:
        return JsonResponse({'error': 'الإشعار غير موجود'}, status=404)


@login_required
def deletedata(request):
    try:
        student = Student.objects.filter(user = request.user).first()
        examdate = ExamStu.objects.filter(student= student).first()
        examdate.delete()
        messages.success(request, "تم حذف الموعد بنجاح")

    except Exception as e:
        messages.error(request, f'حدث خطأ: {e}')
        
    
    return redirect("/dash")
    


@login_required
def exam_log(request):
    student = Student.objects.filter(user=request.user).first()
    exam_log = ExamStu.objects.filter(student=student, date__tarkh__lt= today).order_by("-date__tarkh")
    
    notes = Notes.objects.filter(user=student).all().order_by("-created_at")
    for note in notes:
        note.hijri_created_at = to_hijri(note.created_at)
           
    for exam in exam_log:
        result = ExamRes.objects.filter(date=exam).first()
        if result:
            exam.percentage = int((result.score / 20) *100) or "-"
            exam.memorization_level = dict({"excellent": "ممتاز", "very_good": " جيد جدا", "good": "جيد", "fair": "مقبول", "weak": "ضعيف"}).get(result.memorization_level) or "-"
            exam.tajweed_level = dict({"excellent": "ممتاز", "very_good": " جيد جدا", "good": "جيد", "fair": "مقبول", "weak": "ضعيف"}).get(result.tajweed_level) or "-"
            exam.notes = result.notes or "-"
            exam.hijriDate = to_hijri(result.date.date.tarkh)
        else:
            exam.percentage = 0
            exam.memorization_level = "-"
            exam.tajweed_level = "-"
            exam.notes = "-"
            exam.hijriDate = to_hijri(exam.date.tarkh)
   
    context = {
        'exam_log': exam_log,
        'notes': notes,
    }
    return render(request, 'students/html/exam_log.html', context)

@login_required
def dateView(request, date_id):
    student = Student.objects.filter(user=request.user).first()
    result = ExamStu.objects.filter(student=student, id=date_id).first()
    exam = ExamRes.objects.filter(date=result).first()
    degree = ExamQuestion.objects.filter(exam= exam)
    notes = Notes.objects.filter(user=student).all().order_by("-created_at")
    for note in notes:
        note.hijri_created_at = to_hijri(note.created_at)
           
    exam.percentage = int((exam.score / 20) *100) or "-"
    exam.memorization_level = dict({"excellent": "ممتاز", "very_good": " جيد جدا", "good": "جيد", "fair": "مقبول", "weak": "ضعيف"}).get(exam.memorization_level) or "-"
    exam.tajweed_level = dict({"excellent": "ممتاز", "very_good": " جيد جدا", "good": "جيد", "fair": "مقبول", "weak": "ضعيف"}).get(exam.tajweed_level) or "-"
    exam.notes = exam.notes or "-"
    exam.hijriDate = to_hijri(exam.date.date.tarkh)
   
    context = {
        'exam': exam,
        'notes': notes,
        'degree': degree,
    }
    return render(request, 'students/html/date_view.html', context)


@login_required
def profile(request):
    student = Student.objects.filter(user=request.user).first()
    student.hijri = to_hijri(student.user.birth)
    student.rwia = dict({"hfs": "حفص", "wrsh": "ورش", "qalon": "قالون"}).get(student.rwia)
    student.country = dict(User._meta.get_field('country').choices).get(student.user.country)
    student.t = dict({"track_1": "المساق الأول", "track_2": "المساق الثاني", "track_3": "المساق الثالث"}).get(student.track.name)
    notes = Notes.objects.filter(user=student).all().order_by("-created_at")
    for note in notes:
        note.hijri_created_at = to_hijri(note.created_at)
    
    context = {
        'student': student,
        'notes': notes,
    }
    
    return render(request, 'students/html/profile.html', context)

@login_required
def edit_profile(request):
    student = Student.objects.filter(user=request.user).first()
    notes = Notes.objects.filter(user=student).all().order_by("-created_at")
    for note in notes:
        note.hijri_created_at = to_hijri(note.created_at)

    if request.method == 'POST':
        edit_profile_form = EditProfile(request.POST, instance=request.user)
        if edit_profile_form.is_valid():
            edit_profile_form.save()
            messages.success(request, "تم تعديل البيانات بنجاح")
            return redirect('/dash') 
        else:
            messages.error(request, "حدث خطأ أثناء تعديل البيانات")
            
        
    else:
        edit_profile_form = EditProfile(instance=request.user)
        
    context = {
        'notes': notes,
        'edit_profile_form': edit_profile_form,
    }
    
    return render(request, 'students/html/edit_profile.html', context)


@login_required
def excuse(request):
    student= Student.objects.filter(user= request.user).first()
    notes = Notes.objects.filter(user=student).all().order_by("-created_at")
    for note in notes:
        note.hijri_created_at = to_hijri(note.created_at)
    
    if request.method == 'POST':
        user = Student.objects.filter(user= request.user).first()
        excuse_form = ExcuseForm(request.POST)
        excuse = excuse_form.save(commit=False)
        excuse.user = user
        excuse.save()
        messages.success(request, 'تم إرسال العذر بنجاح')
        send_by_bot(user.user.teleid, 'تم إرسال عذرك بنجاح')
        return redirect('/dash')
        
    else:
        excuse_form = ExcuseForm()

    context = {
        'notes': notes,
        'excuse_form': excuse_form,
        
    }

    return render(request, 'students/html/excuse.html', context)


