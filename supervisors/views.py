from django.forms import modelformset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
import pytz
from accounts.models import User
from exams.models import ExamDate, ExamQuestion, ExamRes, ExamStu
from project.views import ar_time, score, send_note, to_hijri
from sheikhs.models import Sheikh
from students.models import Student
from django.db.models import Avg, Q
from students.views import count_progress
from supervisors.forms import AddDate, EditProfile, StuExamQue, StuExamRes
from supervisors.models import Supervisor
from datetime import date , datetime
from django.utils import timezone
from django.contrib import messages


today = timezone.now() 




@login_required
def supervisor_dash(request):
    supervisor = Supervisor.objects.filter(user=request.user).first()
    sheikhs = Sheikh.objects.filter(supervisor=supervisor)
    all_stu_num = 0
    all_sheikhs_count = sheikhs.count()
    
    
    for sheikh in sheikhs:
        sheikh.stu_count = Student.objects.filter(sheikh=sheikh).count()
        all_stu_num += sheikh.stu_count
        sheikh.com_exams = ExamRes.objects.filter(date__date__sheikh=sheikh, score__gt=0).count()
        sheikh.not_com_exams = ExamStu.objects.filter(date__sheikh=sheikh, exam_res__score= None, date__tarkh__lt=today).count()
        sheikh.avg_exams = ExamRes.objects.filter(date__date__sheikh=sheikh, score__gt=0).aggregate(Avg('score'))['score__avg'] or 0
        sheikh.status = dict(Sheikh._meta.get_field('status').choices).get(sheikh.status)

        
    all_com_exams = ExamRes.objects.filter(date__date__sheikh__supervisor=supervisor, score__gt=0).count()
    all_not_com_exams = ExamStu.objects.filter(date__sheikh__supervisor=supervisor, exam_res__score =None, date__tarkh__lt=today).count()
    all_avg_exams = ExamRes.objects.filter(date__date__sheikh__supervisor=supervisor, score__gt=0).aggregate(Avg('score'))['score__avg']

    context = {
        "all_sheikhs_count": all_sheikhs_count if all_sheikhs_count else 0,
        "all_stu_num": all_stu_num,
        "all_com_exams": all_com_exams if all_com_exams else 0,
        "all_not_com_exams": all_not_com_exams if all_not_com_exams else 0,
        "all_avg_exams": all_avg_exams if all_avg_exams else 0,
        "sheikhs": sheikhs,
        "supervisor": supervisor,
    }
    return render(request, "supervisors/html/supervisor_dash.html", context)


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
    
    
    return render(request, "supervisors/html/student_search.html")


@login_required
def stu_dash(request, code):
    student = Student.objects.filter(user__code=code).first()
    student.status = dict({"active": "نشط", 
                                "need_help": "محتاج متابعة", 
                                "withdrawn": "منسحب", 
                                "graduated": "متخرج", 
                                "excluded": "معتذر مؤقتا"}).get(student.status)
    
    student.progress = count_progress(student.track.name, student.nsap)
    s = ExamRes.objects.filter(date__student=student).last() or 0 
    if s :
        student.lastScore = (s.score/ 20) * 100
    else:
        student.lastScore = 0
        
    
    next = ExamStu.objects.filter(student=student, date__tarkh__gt=today).first()
    student.nextExam= to_hijri(next.date.tarkh) if next else "لا يوجد"

    
    exam_log = ExamStu.objects.filter(student=student)
    for exam in exam_log:
        result = ExamRes.objects.filter(date=exam).first()
        if result and result.score != 0:
            exam.percentage = int((result.score / 20) *100)
            exam.memorization_level = dict(ExamRes._meta.get_field('memorization_level').choices).get(result.memorization_level)
            print(dict(ExamRes._meta.get_field('memorization_level').choices))
            exam.tajweed_level = dict(ExamRes._meta.get_field('memorization_level').choices).get(result.tajweed_level)
            exam.status = dict(ExamRes._meta.get_field('status').choices).get(result.status)
            exam.hijriDate =  to_hijri(exam.date.tarkh)
        else:
            exam.percentage = 0
            exam.memorization_level = "-"
            exam.tajweed_level = "-"
            exam.status = '-'
            exam.hijriDate =  to_hijri(exam.date.tarkh)
    try:
        last_exam = ExamRes.objects.filter(student=student).last()
    except:
        last_exam = None
    
    context = {
        'student': student,
        'exam_log': exam_log,
        'last_score': round(((last_exam.score / 20) *100), 2) if last_exam else 0,

    }
    return render(request, "supervisors/html/stu_dash.html", context)
    

@login_required
def next_exams(request):
    supervisor = Supervisor.objects.select_related('user').filter(user=request.user).first()
    sheikhs = Sheikh.objects.filter(supervisor=supervisor).all()
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
    return render(request, "supervisors/html/next_exams.html", context)
    
    

@login_required
def my_students(request):
    supervisor = Supervisor.objects.select_related('user').filter(user=request.user).first()
    sheikhs = Sheikh.objects.filter(supervisor=supervisor).all()
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
    return render(request, "supervisors/html/my_students.html", context)
  


@login_required
def com_exam(request):
    supervisor = Supervisor.objects.select_related('user').filter(user=request.user).first()
    dates = ExamRes.objects.filter(date__date__sheikh__supervisor = supervisor, score__gt= 0).all().order_by('date__date__tarkh')
    for date in dates:
        date.hijri = to_hijri(date.date.date.tarkh)
        date.from_hour = ar_time(date.date.date.from_hour)
        date.to_hour = ar_time(date.date.date.to_hour)
        date.memorization_level = dict(ExamRes._meta.get_field('memorization_level').choices).get(date.memorization_level)
        date.tajweed_level = dict(ExamRes._meta.get_field('tajweed_level').choices).get(date.tajweed_level)
    
    query = request.GET.get('q', '')
    
    if query:
        results = ExamRes.objects.filter(date__date__sheikh__supervisor = supervisor, score__gt= 0, date__date__tarkh__lt=today, date__student__user__name__icontains = query).all()
        data = {
            "results": [{"name": p.date.student.user.name,
                         "date": to_hijri(p.date.date.tarkh) , 
                         "score": p.score, 
                         "memorization_level": dict(ExamRes._meta.get_field("memorization_level").choices).get(p.memorization_level), 
                         "tajweed_level": dict(ExamRes._meta.get_field("memorization_level").choices).get(p.tajweed_level),
                         "id": p.date.id,
                         "code": p.date.student.user.code,
                         } for p in results]
        }
        return JsonResponse(data)


    context ={
        'dates': dates
    }
    return render(request, 'supervisors/html/com_exam.html',context)



@login_required
def not_com_exams(request, ):
    supervisor = Supervisor.objects.select_related('user').filter(user=request.user).first()
    dates = ExamStu.objects.filter(date__sheikh__supervisor=supervisor, exam_res__score= None, date__tarkh__lt=today).all().order_by('date__tarkh')
    for date in dates:
        date.hijri = to_hijri(date.date.tarkh)
        date.from_hour = ar_time(date.date.from_hour)
        date.to_hour = ar_time(date.date.to_hour)
    
    query = request.GET.get('q', '')
    
    if query:
        results = ExamStu.objects.filter(date__sheikh__supervisor=supervisor, exam_res__score= None, date__tarkh__lt=today ,student__user__name__icontains = query).all()
        data = {
            "results": [{"name": p.student.user.name,
                         "date": to_hijri(p.date.tarkh) , 
                         "sheikh": p.date.sheikh.user.name, 
                         "id": p.date.id,
                         "code": p.student.user.code,
                         } for p in results]
        }
        print(date)
        return JsonResponse(data)


    context ={
        'dates': dates
    }
    return render(request, 'supervisors/html/not_com_exams.html',context)




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
        'stu_res_form':stu_res_form,
        'num_ques': num_ques,
        'stu_que_form':stu_que_form,
    }
    return render(request, 'supervisors/html/stu_res.html',context)


  

@login_required
def sheikh_dash(request, sheikh_code):
    sheikh = Sheikh.objects.filter(user__code=sheikh_code).first()
    sheikh.country = dict(User._meta.get_field('country').choices).get(sheikh.user.country)
    sheikh.hijri = to_hijri(sheikh.user.birth)
    sheikh.rwia = dict({"hfs": "حفص", "wrsh": "ورش", "qalon": "قالون"}).get(sheikh.rwia )
    context = {
        "sheikh": sheikh,
    }
    return render(request, "supervisors/html/sheikh_dash.html", context)
    

@login_required
def add_date(request, sheikh_code):
    sheikh = Sheikh.objects.filter(user__code=sheikh_code).first()
    
    if request.method == "POST":
        add_date_form = AddDate(request.POST)
        if add_date_form.is_valid():
            form = add_date_form.save(commit=False)
            form.sheikh = sheikh
            form.save()
            messages.success(request, "تم إضافة الموعد بنجاح")
            return redirect(request.path.replace("add", "dates"))
        
    else:
        add_date_form = AddDate()
    
    context = {
        "add_date_form": add_date_form,
    }
    return render(request, "supervisors/html/add_date.html", context)


@login_required
def view_dates(request, sheikh_code):
    sheikh = Sheikh.objects.filter(user__code=sheikh_code).first()
    dates = ExamDate.objects.filter(sheikh=sheikh).order_by('-tarkh')
    if dates:
        for date in dates:
            date.hijri = to_hijri(date.tarkh)
            date.from_hour = ar_time(date.from_hour)
            date.to_hour = ar_time(date.to_hour)
            num_book_stu = ExamStu.objects.filter(date=date).count()
            date.remain = date.student_num - num_book_stu
    context = {
        "dates": dates,
        "sheikh": sheikh,
    }
    return render(request, "supervisors/html/sheikh_dates.html", context)



@login_required
def view_date(request, date_id, sheikh_code):
    students = Student.objects.filter(examstu__date__id=date_id, examstu__date__sheikh__user__code=sheikh_code)
    date = ExamStu.objects.filter(date__id=date_id).first()
    
    context ={
        'students': students if students else None,
        'date': date
    }
    return render(request, 'supervisors/html/date_stu.html',context)


@login_required
def edit_date(request, sheikh_code, date_id):
    sheikh = get_object_or_404(Sheikh, user__code=sheikh_code)
    date = get_object_or_404(ExamDate, id=date_id, sheikh=sheikh)
    
    if request.method == "POST":
        edit_date_form = AddDate(request.POST, instance=date)
        if edit_date_form.is_valid():
            form = edit_date_form.save(commit=False)
            form.sheikh = sheikh
            form.save()
            messages.success(request, "تم تعديل الموعد بنجاح")
            return redirect(request.path.replace(f"{date_id}/edit_date", "dates"))
        
    else:
        edit_date_form = AddDate(instance=date)
    
    context = {
        "edit_date_form": edit_date_form,
    }
    return render(request, "supervisors/html/edit_date.html", context)
    
    
  

@login_required
def profile(request):
    supervisor = Supervisor.objects.select_related('user').filter(user=request.user).first()
    supervisor.country = dict(User._meta.get_field('country').choices).get(supervisor.user.country)
    supervisor.hijri = to_hijri(supervisor.user.birth)
    context = {
        "supervisor": supervisor,
    }
    return render(request, "supervisors/html/profile.html", context)
    
    

@login_required
def editprofile(request):
    if request.method == "POST":
        edit_profile_form = EditProfile(request.POST,instance=request.user)
        if edit_profile_form.is_valid():
            edit_profile_form.save()
            messages.success(request, "تم تعديل بياناتك بنجاح")
            return redirect('/dash')
        
    else:
        edit_profile_form = EditProfile(instance=request.user)
    
    context = {
        "edit_profile_form": edit_profile_form,
    }
    return render(request, "supervisors/html/edit_profile.html", context)
    
    
    
    
    
    
