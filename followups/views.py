from math import floor
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Avg, Q
import pytz
from accounts.models import User
from exams.models import ExamDate, ExamQuestion, ExamRes, ExamStu
from followups.forms import AddSheikh, AddStudent, AddSupervisor
from project.views import ar_time, send_by_bot, send_note, to_hijri
from sheikhs.models import Sheikh
from students.models import Student
from students.views import count_progress
from supervisors.forms import StuExamQue, StuExamRes
from supervisors.models import Supervisor
from .models import FollowUpSupervisor
from django.contrib.auth.decorators import login_required
from datetime import date , datetime
from django.utils import timezone
from django.contrib import messages

# Create your views here.

today = timezone.now() 


@login_required
def followup_dash(request):
    followup = FollowUpSupervisor.objects.filter(user=request.user).first()
    supervisors = Supervisor.objects.filter(followup_supervisor=followup)
    supervisor_num = supervisors.count()  
    
    sheikhs_num = Sheikh.objects.filter(supervisor__followup_supervisor=followup).count()
    student= Student.objects.filter(sheikh__supervisor__followup_supervisor =followup).all()
    com_exam = ExamRes.objects.filter(score__gt = 0, date__student__in=student).count()
    not_com_exam = ExamRes.objects.filter(score= 0, date__student__in=student).count()
    avg_score = ExamRes.objects.filter(score__gt= 0, date__student__in=student).aggregate(Avg('score'))['score__avg']
    
    for supervisor in supervisors:
        sheikhs = Sheikh.objects.filter(supervisor=supervisor)
        supervisor.sheikh_count = sheikhs.count()
        supervisor.com_exams = ExamRes.objects.filter(date__date__sheikh__supervisor=supervisor, score__gt=0).count()
        supervisor.not_com_exams = ExamStu.objects.filter(date__sheikh__supervisor=supervisor, exam_res__score= None, date__tarkh__lt=today).count()
        supervisor.status = dict(Supervisor._meta.get_field('status').choices).get(supervisor.status)
        supervisor.avg_exams = 0
        
        for sheikh in sheikhs:
            avg_exams = ExamRes.objects.filter(date__date__sheikh=sheikh, score__gt=0).aggregate(Avg('score'))['score__avg'] or 0
            supervisor.avg_exams += avg_exams
    
    context = {
        "followup": followup,
        "supervisors": supervisors,
        "supervisor_num":supervisor_num,
        "sheikhs_num": sheikhs_num,
        "com_exam": com_exam,
        "not_com_exam":not_com_exam,
        "avg_score": avg_score or 0,
    }
    return render(request, 'followups/html/followup_dash.html', context)


@login_required
def student_search(request):
    
    q = request.GET.get('q','')
    if q:
        students = Student.objects.filter(Q(user__name__icontains=q) |
                                        Q(user__tele__icontains=q) | 
                                        Q(user__email__icontains=q) & 
                                        Q(user__gender=request.user.gender)).all()
        data = {
            "students": [{"name": stu.user.name, 
                          "status": dict(Student._meta.get_field('status').choices).get(stu.status), 
                          "sheikh": stu.sheikh.user.name if stu.sheikh.user.name else '-', 
                          "tele": stu.user.tele, 
                          "code": stu.user.code} for stu in students]
        }
        
        return JsonResponse(data)
    
    
    return render(request, "followups/html/student_search.html")



@login_required
def stu_dash(request, code):
    student = Student.objects.filter(user__code=code).first()
    progress = count_progress(student.track.name, student.nsap)
    try:
        next_exam_obj = ExamStu.objects.filter(student=student, date__tarkh__gt=today).order_by('date__tarkh').first()
        next_exam_by_hijri = to_hijri(next_exam_obj)
    except:
        next_exam_by_hijri = "لا يوجد"
    
    exam_log = ExamStu.objects.filter(student=student)
    for exam in exam_log:
        result = ExamRes.objects.filter(date=exam).first()
        if result and result.score != 0:
            exam.percentage = int((result.score / 20) *100)
            exam.memorization_level = dict(ExamRes._meta.get_field('memorization_level').choices).get(result.memorization_level)
            print(dict(ExamRes._meta.get_field('memorization_level').choices))
            exam.tajweed_level = dict(ExamRes._meta.get_field('memorization_level').choices).get(result.tajweed_level)
            exam.status = dict(ExamRes._meta.get_field('status').choices).get(result.status) if result.status else "-"
            exam.exdate =  to_hijri(exam.date.tarkh)
        else:
            exam.percentage = 0
            exam.memorization_level = "-"
            exam.tajweed_level = "-"
            exam.status = '-'
            exam.exdate =  to_hijri(exam.date.tarkh)
    try:
        last_exam = ExamRes.objects.filter(student=student).last()
    except:
        last_exam = None
    
    context = {
        'student': student,
        'progress': progress,
        'exam_log': exam_log,
        'next_exam_by_hijri':next_exam_by_hijri,
        'last_score': round(((last_exam.score / 20) *100), 2) if last_exam else 0,

    }
    return render(request, "followups/html/stu_dash.html", context)
    


@login_required
def next_exams(request):
    followup = FollowUpSupervisor.objects.select_related('user').filter(user=request.user).first()
    sheikhs = Sheikh.objects.filter(supervisor__followup_supervisor=followup).all()
    dates = ExamDate.objects.filter(sheikh__in=sheikhs, tarkh__gte=today).all().order_by('tarkh')
    if dates:
        for date in dates:
            date.hijri = to_hijri(date.tarkh)
            date.from_hour = ar_time(date.from_hour)
            date.to_hour = ar_time(date.to_hour)
            num_book_stu = ExamStu.objects.filter(date=date).count()
            date.remain = (date.student_num or 0) - num_book_stu
    
    context = {
        "dates": dates,
    }
    return render(request, "followups/html/next_exams.html", context)
    

   

@login_required
def my_students(request):
    followup = FollowUpSupervisor.objects.select_related('user').filter(user=request.user).first()
    sheikhs = Sheikh.objects.filter(supervisor__followup_supervisor=followup).all()
    students = Student.objects.filter(sheikh__in=sheikhs).all().order_by('sheikh')
    for stu in students:
        stu.status = dict({"active": "نشط", 
                           "need_help": "محتاج متابعة", 
                           "excluded": "مستبعد", 
                           "withdrawn": "منسحب", 
                           "graduated": "متخرج"}).get(stu.status)
    
    
    q = request.GET.get('q','')
    if q:
        students = Student.objects.filter(Q(user__name__icontains=q) |
                                        Q(user__tele__icontains=q) | 
                                        Q(user__email__icontains=q) & 
                                        Q(user__gender=request.user.gender)).all()
        data = {
            "students": [{"name": stu.user.name, 
                          "status": dict({"active": "نشط", "need_help": "محتاج متابعة", "excluded": "مستبعد", "withdrawn": "منسحب", "graduated": "متخرج"}).get(stu.status), 
                          "sheikh": stu.sheikh.user.name if stu.sheikh.user.name else '-', 
                          "tele": stu.user.tele, 
                          "code": stu.user.code} for stu in students]
        }
        
        return JsonResponse(data)

    context = {
        "students": students,
    }
    return render(request, "followups/html/my_students.html", context)
  

@login_required
def my_students_add(request):
    followup = FollowUpSupervisor.objects.select_related('user').filter(user=request.user).first()
    sheikhs = Sheikh.objects.filter(supervisor__followup_supervisor=followup).all()
    students = Student.objects.filter(sheikh__in=sheikhs).all().order_by('sheikh')
    if request.method == "POST":
        
        student_instance = None
        if 'user' in request.POST:
            student_instance = Student.objects.filter(user=request.POST['user']).first()
            sheikh = Sheikh.objects.filter(user=request.POST['sheikh']).first()

        add_student_form = AddStudent(request.POST, user=followup, instance=student_instance)
        if add_student_form.is_valid():
            form = add_student_form.save(commit=False)
            form.shiekh = sheikh
            form.save()
            messages.success(request, 'تم إضافة الطالب بنجاح')
            return redirect("/followup_dash/my_students/")
            

    else:
        add_student_form = AddStudent(user=followup)
    
    context = {
        "add_student_form": add_student_form,
    }
    return render(request, "followups/html/my_students_add.html", context)
  
    

   

@login_required
def my_sheikhs(request):
    followup = FollowUpSupervisor.objects.select_related('user').filter(user=request.user).first()
    sheikhs = Sheikh.objects.filter(supervisor__followup_supervisor=followup).all()
    for sheikh in sheikhs:
        sheikh.status = dict({"active": "نشط", 
                           "need_help": "محتاج متابعة", 
                           "withdrawn": "منسحب", 
                           "excused": "معتذر مؤقتا"}).get(sheikh.status)
        sheikh.rwia = dict({"hfs": "حفص", 
                           "wrsh": "ورش", 
                           "qalon": "قالون"}).get(sheikh.rwia)
    
    
    q = request.GET.get('q','')
    if q:
        sheikhs = Sheikh.objects.filter(Q(user__name__icontains=q) |
                                        Q(user__tele__icontains=q) | 
                                        Q(supervisor__user__name__icontains=q) | 
                                        Q(rwia__icontains=q) | 
                                        Q(user__email__icontains=q) & 
                                        Q(user__gender=request.user.gender)).all()
        data = {
            "sheikhs": [{"name": sheikh.user.name, 
                         "supervisor": sheikh.supervisor.user.name,
                         "status": dict({"active": "نشط", 
                                            "need_help": "محتاج متابعة", 
                                            "withdrawn": "منسحب", 
                                            "excused": "معتذر مؤقتا"}).get(sheikh.status), 
                          "rwia": dict({"hfs": "حفص", "wrsh": "ورش", "qalon": "قالون"}).get(sheikh.rwia) if sheikh.rwia else '-', 
                          "tele": sheikh.user.tele, 
                          "code": sheikh.user.code} for sheikh in sheikhs]
        }
        
        return JsonResponse(data)

    context = {
        "sheikhs": sheikhs,
    }
    return render(request, "followups/html/my_sheikhs.html", context)
  

@login_required
def my_sheikhs_add(request):
    followup = FollowUpSupervisor.objects.select_related('user').filter(user=request.user).first()
    
    if request.method == "POST":
        
        add_sheikh_form = AddSheikh(request.POST, user=followup)
        if add_sheikh_form.is_valid():
            add = add_sheikh_form.save(commit=False)
            user = add_sheikh_form.cleaned_data['user']
            user_up = User.objects.get(id=user.id)
            user_up.role = "sheikh"
            user_up.save()
            add.save()
            
            messages.success(request, 'تم إضافة الشيخ بنجاح')
            try:
                send_by_bot(user_up.teleid, f'''
حياك الله {user_up.name}

تم ترقيتك لتكون شيخ معنا في معهد إحياء

وفقك الله وبارك فيك
                            
                            ''')
            except:
                pass
            return redirect("/followup_dash/my_sheikhs/")
            
    else:
        add_sheikh_form = AddSheikh(user=followup)
    
    context = {
        "add_sheikh_form": add_sheikh_form,
    }
    return render(request, "followups/html/my_sheikhs_add.html", context)

@login_required
def sheikh_dash(request, sheikh_code):
    sheikh = Sheikh.objects.filter(user__code=sheikh_code).first()
    sheikh.country = dict(User._meta.get_field('country').choices).get(sheikh.user.country)
    sheikh.hijri = to_hijri(sheikh.user.birth)
    sheikh.rwia = dict({"hfs": "حفص", "wrsh": "ورش", "qalon": "قالون"}).get(sheikh.rwia )
    
    sheikh.stu_num = Student.objects.filter(sheikh= sheikh).count()
    sheikh.need_help_num = Student.objects.filter(sheikh= sheikh, status='need_help').count()
    sheikh.complete_exam= ExamRes.objects.filter(date__date__sheikh=sheikh, score__gt=0).count()
    sheikh.not_complete_exam= ExamRes.objects.filter(date__date__sheikh=sheikh, score=0).count()
    average_score = ExamRes.objects.filter(date__date__sheikh=sheikh, score__gt=0).aggregate(Avg('score'))['score__avg']
    sheikh.average_score = floor((average_score / 20) * 100) if average_score else 0
    next_sheikh_dates = ExamDate.objects.filter(sheikh=sheikh, tarkh__gte=today)
    if next_sheikh_dates:
        for date in next_sheikh_dates:
            date.hijri = to_hijri(date.tarkh)
            date.from_hour = ar_time(date.from_hour)
            date.to_hour = ar_time(date.to_hour)
            num_book_stu = ExamStu.objects.filter(date=date).count()
            date.remain = date.student_num - num_book_stu
            
    context = {
        "sheikh": sheikh,
        "next_sheikh_dates":next_sheikh_dates,
    }
    return render(request, "followups/html/sheikh_dash.html", context)
  
    
@login_required
def view_date(request, date_id, sheikh_code):
    students = Student.objects.filter(examstu__date__id=date_id, examstu__date__sheikh__user__code=sheikh_code)
    for stu in students:
        date = ExamRes.objects.filter(date__student__user__code=stu.user.code, date__date__id= date_id).first()
        try:
            stu.score = date.score or "-"
        except:
            stu.score = "-"
            
    context ={
        'students': students if students else None,
        'date_id': date_id
    }
    return render(request, 'followups/html/date_stu.html',context)

  
    

   

@login_required
def my_supervisors(request):
    followup = FollowUpSupervisor.objects.select_related('user').filter(user=request.user).first()
    supervisors = Supervisor.objects.filter(followup_supervisor=followup).all()
    for supervisor in supervisors:
        supervisor.status = dict({"active": "نشط", 
                           "need_help": "محتاج متابعة", 
                           "withdrawn": "منسحب", 
                           "excused": "معتذر مؤقتا"}).get(supervisor.status)
        supervisor.sheikhs_num = Sheikh.objects.filter(supervisor=supervisor).count()
        supervisor.students_num = Student.objects.filter(sheikh__supervisor=supervisor).count()
    
    
    q = request.GET.get('q','')
    if q:
        supervisors = Supervisor.objects.filter(Q(user__name__icontains=q) |
                                        Q(user__tele__icontains=q) | 
                                        Q(user__email__icontains=q) & 
                                        Q(user__gender=request.user.gender)).all()
        data = {
            "supervisors": [{"name": supervisor.user.name, 
                         "status": dict({"active": "نشط", 
                                            "need_help": "محتاج متابعة", 
                                            "withdrawn": "منسحب", 
                                            "excused": "معتذر مؤقتا"}).get(supervisor.status), 
                          "tele": supervisor.user.tele, 
                          "sheikhs_num": Sheikh.objects.filter(supervisor=supervisor).count(), 
                          "students_num": Student.objects.filter(sheikh__supervisor=supervisor).count(), 
                          "code": supervisor.user.code} for supervisor in supervisors]
        }
        
        return JsonResponse(data)

    context = {
        "supervisors": supervisors,
    }
    return render(request, "followups/html/my_supervisors.html", context)
  

@login_required
def my_supervisors_add(request):
    followup = FollowUpSupervisor.objects.select_related('user').filter(user=request.user).first()
    
    if request.method == "POST":
        add_supervisor_form = AddSupervisor(request.POST)
        if add_supervisor_form.is_valid():
            add = add_supervisor_form.save(commit=False)
            user = add_supervisor_form.cleaned_data['user']
            user_up = User.objects.get(id=user.id)
            user_up.role = "supervisor"
            user_up.save()
            add.followup_supervisor = followup
            add.save()
            
            messages.success(request, 'تم إضافة المشرف بنجاح')
            try:
                send_by_bot(user_up.teleid, f'''
حياك الله {user_up.name}

تم ترقيتك لتكون مشرف معنا في معهد إحياء

وفقك الله وبارك فيك
                            
                            ''')
            except:
                pass
            return redirect("/followup_dash/my_supervisors/")
            
    else:
        add_supervisor_form = AddSupervisor()
    
    context = {
        "add_supervisor_form": add_supervisor_form,
    }
    return render(request, "followups/html/my_supervisors_add.html", context)



@login_required
def supervisor_dash(request, supervisor_code):
    supervisor = Supervisor.objects.filter(user__code=supervisor_code).first()
    sheikhs = Sheikh.objects.filter(supervisor=supervisor)
    
    for sheikh in sheikhs:
        sheikh.rwia = dict({"hfs": "حفص", "wrsh": "ورش", "qalon": "قالون"}).get(sheikh.rwia)
        sheikh.status = dict({"active": "نشط", "need_help": "محتاج متابعة", "withdrawn": "منسحب", "excused": "معتذر مؤقتا"}).get(sheikh.status)
        sheikh.stu_count = Student.objects.filter(sheikh=sheikh).count()
        sheikh.com_exams = ExamRes.objects.filter(date__date__sheikh=sheikh, score__gt=0).count()
        sheikh.not_com_exams = ExamStu.objects.filter(date__sheikh=sheikh, exam_res__score= None, date__tarkh__lt=today).count()
        sheikh.avg_exams = ExamRes.objects.filter(date__date__sheikh=sheikh, score__gt=0).aggregate(Avg('score'))['score__avg'] or 0


    
    
    supervisor.country = dict(User._meta.get_field('country').choices).get(supervisor.user.country)
    supervisor.hijri = to_hijri(supervisor.user.birth)
    
    supervisor.stu_num = Student.objects.filter(sheikh__supervisor= supervisor).count()
    supervisor.need_help_num = Student.objects.filter(sheikh__supervisor= supervisor, status='need_help').count()
    supervisor.complete_exam = ExamRes.objects.filter(date__date__sheikh__supervisor=supervisor, score__gt=0).count()
    supervisor.not_complete_exam = ExamRes.objects.filter(date__date__sheikh__supervisor=supervisor, score=0).count()
    supervisor.average_score = ExamRes.objects.filter(date__date__sheikh__supervisor=supervisor, score__gt=0).aggregate(Avg('score'))['score__avg']
    if supervisor.average_score:
        supervisor.average_score_per = floor((supervisor.average_score / 20) * 100)
    else:
        supervisor.average_score_per = 0
            
    context = {
        "supervisor": supervisor,
        "sheikhs": sheikhs,
    }
    return render(request, "followups/html/supervisor_dash.html", context)
  











@login_required
def com_exam(request):
    followup = FollowUpSupervisor.objects.select_related('user').filter(user=request.user).first()
    dates = ExamRes.objects.filter(date__date__sheikh__supervisor__followup_supervisor = followup, score__gt= 0).all().order_by('student')
    for date in dates:
        date.hijri = to_hijri(date.date.date.tarkh)
        date.from_hour = ar_time(date.date.date.from_hour)
        date.to_hour = ar_time(date.date.date.to_hour)
        date.memorization_level = dict(ExamRes._meta.get_field('memorization_level').choices).get(date.memorization_level)
        date.tajweed_level = dict(ExamRes._meta.get_field('tajweed_level').choices).get(date.tajweed_level)
    
    query = request.GET.get('q', '')
    
    if query:
        results = ExamRes.objects.filter(date__date__sheikh__supervisor__followup_supervisor = followup, score__gt= 0, date__date__tarkh__lt=today ,student__user__name__icontains = query).all()
        data = {
            "results": [{"name": p.student.user.name,
                         "date": to_hijri(p.date.date.tarkh) , 
                         "score": p.score, 
                         "memorization_level": dict(ExamRes._meta.get_field("memorization_level").choices).get(p.memorization_level), 
                         "tajweed_level": dict(ExamRes._meta.get_field("memorization_level").choices).get(p.tajweed_level),
                         "id": p.date.date.id,
                         "code": p.student.user.code,
                         } for p in results]
        }
        return JsonResponse(data)


    context ={
        'dates': dates
    }
    return render(request, 'followups/html/com_exam.html',context)


@login_required
def not_com_exams(request):
    followup = FollowUpSupervisor.objects.select_related('user').filter(user=request.user).first()
    dates = ExamRes.objects.filter(date__date__sheikh__supervisor__followup_supervisor = followup, score= 0, date__date__tarkh__lt=today).all().order_by('date__date__tarkh')
    for date in dates:
        date.hijri = to_hijri(date.date.date.tarkh)
        date.from_hour = ar_time(date.date.date.from_hour)
        date.to_hour = ar_time(date.date.date.to_hour)
        date.memorization_level = "-"
        date.tajweed_level = "-"
        date.score = "-"
    
    query = request.GET.get('q', '')
    
    if query:
        results = ExamRes.objects.filter(date__date__sheikh__supervisor__followup_supervisor = followup, score= 0, date__date__tarkh__lt=today ,student__user__name__icontains = query).all()
        data = {
            "results": [{"name": p.student.user.name,
                         "sheikh": p.student.sheikh.user.name,
                         "date": to_hijri(p.date.date.tarkh) , 
                         "score": "-", 
                         "memorization_level": "-", 
                         "tajweed_level": "-",
                         "id": p.date.date.id,
                         "code": p.student.user.code,
                         } for p in results]
        }
        return JsonResponse(data)


    context ={
        'dates': dates
    }
    return render(request, 'followups/html/not_com_exams.html',context)




@login_required
def stu_res(request,date_id ,stu_code):
    student = get_object_or_404(Student, user__code= stu_code)
    date_stu = get_object_or_404(ExamStu, date__id= date_id, student= student)
    prev_res = ExamRes.objects.filter(date= date_stu, date__student= student).first() if date else ExamRes.objects.none()
    prev_ques = ExamQuestion.objects.filter(exam= prev_res) if prev_res else ExamQuestion.objects.none()
    num_ques = date_stu.stage.num_ques
    prev_ques_num = prev_ques.count()
    extra_que = max(num_ques - prev_ques_num, 0)
    StuExamQueFormSet = modelformset_factory(ExamQuestion, form=StuExamQue, extra=extra_que)
    
    
    if request.method == 'POST':
        stu_res_form = StuExamRes(request.POST, instance=prev_res)
        stu_que_form = StuExamQueFormSet(request.POST, queryset= prev_ques)
        if stu_res_form.is_valid() and stu_que_form.is_valid():
            save_res = stu_res_form.save(commit=False)
            save_res.student = student
            save_res.date = date_stu
            score = 20 - ((sum(q.cleaned_data.get('mistake_count', 0) or 0 for q in stu_que_form) * 1) + (sum(q.cleaned_data.get("alarm_count", 0) or 0 for q in stu_que_form) * 0.25))
            save_res.score = score
            save_res.status = "passed" if score >= 10 else "Failed"  
            save_res.save()
            
            
 
            for i, form in enumerate(stu_que_form):
                save_que = form.save(commit=False)
                save_que.exam = save_res
                save_que.question_number = i + 1
                save_que.save()
        
            hijri = to_hijri(date_stu.date.tarkh)
            messages.success(request, 'تم حفظ الدرجة بنجاح')  
            send_note(student, "حفظ نتيجة اختبار", f'''
حياك الله {student.user.name} 
تم حفظ نتيجة اختبارك بتاريخ {hijri} بنجاح
                      
                      ''')
            return redirect("/sheikh_dash/com_exam/") 
                
    else:
        stu_res_form = StuExamRes(instance=prev_res)
        stu_que_form = StuExamQueFormSet(queryset= prev_ques)

    context ={
        'student': student,
        "date_stu": to_hijri(date_stu.date.tarkh),
        'stu_res_form':stu_res_form,
        'num_ques': num_ques,
        'stu_que_form':stu_que_form,
    }
    return render(request, 'followups/html/stu_res.html',context)





@login_required
def profile(request):
    followup = FollowUpSupervisor.objects.select_related('user').filter(user=request.user).first()
    followup.country = dict(User._meta.get_field('country').choices).get(followup.user.country)
    followup.hijri = to_hijri(followup.user.birth)
    context = {
        "followup": followup,
    }
    return render(request, "followups/html/profile.html", context)
    


