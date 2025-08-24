from datetime import datetime
from django.shortcuts import redirect, render
import requests

from exams.models import ExamQuestion, ExamRes, ExamStu
from sheikhs.models import Sheikh
from students.models import Notes, Student
from tracks.models import Batch
from .forms import ContactUsForm, UserForm, StudentForm
from django.contrib.auth.decorators import login_required
from hijri_converter import Gregorian # type: ignore
from django.contrib import messages
import string
import secrets

def generate_code():
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))



BOT_TOKEN = ""

def send_by_bot(chat_id, message):
    bot_token = BOT_TOKEN
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()  
        print("تم الإرسال:", response.json())
    except requests.exceptions.RequestException as e:
        print("فشل الإرسال إلى تليجرام:", e)


DAYS_AR = {
                    'Saturday': 'السبت',
                    'Sunday': 'الأحد',
                    'Monday': 'الإثنين',
                    'Tuesday': 'الثلاثاء',
                    'Wednesday': 'الأربعاء',
                    'Thursday': 'الخميس',
                    'Friday': 'الجمعة',
                }

def send_note(student, title, message):
    Notes.objects.create(user= student, title = title, message = message)
    send_by_bot(student.user.teleid, f'''
{title}

{message}                
                ''')


def to_hijri(date):
    day_name_en = date.strftime('%A')
    day_name_ar = DAYS_AR.get(day_name_en, '')
    hijri_date = Gregorian(date.year, date.month, date.day).to_hijri()
    try:
        hijri_datetime = f"{date.hour}:{date.minute} - {day_name_ar} {hijri_date.day}/{hijri_date.month}/{hijri_date.year} هـ"
    except:
        hijri_datetime = f"{day_name_ar} {hijri_date.day}/{hijri_date.month}/{hijri_date.year} هـ"
    return hijri_datetime


def ar_time(time):
    if type(time) == str:
        time_24h = datetime.strptime(time, '%H:%M')
    else:
        time_24h = time
    time_12h = time_24h.strftime('%I:%M')
    am_pm = time_24h.strftime('%p')
    
    if am_pm == 'AM':
        time_12h += ' ص'
    else:
         time_12h += ' م'
         
    return time_12h
    


def score(date_id, stu_code):
    ques = ExamQuestion.objects.filter(exam__date__date__id= date_id, exam__student__user__code= stu_code)
    mistake = sum(q.mistake_count for q in ques) * 1 
    alarm = sum(q.alarm_count for q in ques) * 0.25
    total = alarm + mistake
    score = 20 - total
    return score






def home(request):
    if request.user.is_authenticated:
        return redirect('/dash')
    else:
        stu_active = Student.objects.filter(status="active").count() or 0
        stu_graduated = Student.objects.filter(status="graduated").count() or 0
        sheikh_active = Sheikh.objects.filter(status="active").count() or 0
        batchs_num = Batch.objects.count() or 0
        
        context = {
            "stu_active": stu_active,
            "stu_graduated": stu_graduated,
            "sheikh_active": sheikh_active,
            "batchs_num": batchs_num,
        }
        
        return render(request, "html/home.html", context)




def signup(request):
    if request.user.is_authenticated:
            return redirect('/dash')
    else:
        if request.method == 'POST':
            User_form = UserForm(request.POST)
            student_form = StudentForm(request.POST)
            if User_form.is_valid():
                user = User_form.save(commit=False)
                user.code = generate_code()
                user.save()
                if student_form.is_valid():
                    student = student_form.save(commit=False)
                    student.user = user
                    student.save()
                    return redirect('/dash')
        else:
            User_form = UserForm()
            student_form = StudentForm()
            
        context = {
            'User_form' : User_form,
            'student_form' : student_form,
            
        } 
            
        return render(request, "registration/signup.html", context)


def home_redirect(request):
    if request.user.is_authenticated:
        role = request.user.role 
        if role == 'student':
            return redirect('student_dash')
        elif role == 'sheikh':
            return redirect('/sheikh_dash')
        elif role == 'supervisor':
            return redirect('supervisor_dash')
        elif role == 'followup':
            return redirect('followup_dash')
        elif role == 'admin':
            return redirect('/admin')
    return render(request, 'html/home.html')

def FAQ(request):
    return render(request, 'students/html/FAQ.html')

def contact_us(request):
    if request.user.is_authenticated:
        return redirect('/dash')
    else:
        if request.method == 'POST':
            contact_us_form = ContactUsForm(request.POST)
            if contact_us_form.is_valid:
                contact_us_form.save()
                messages.success(request, 'تم إرسال رسالتك بنجاح')
                redirect('/dash')
 
        else:
            contact_us_form = ContactUsForm()
            
        context = {
            'contact_us_form': contact_us_form,
            
        }
            
        return render(request, 'html/contact_us.html', context)


def custom_404(request, exception):
    return render(request, 'html/404.html', status=404)

def custom_500(request):
    return render(request, 'html/500.html', status=500)






