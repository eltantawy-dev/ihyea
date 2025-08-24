from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg
from accounts.models import User
from exams.models import ExamDate, ExamQuestion, ExamRes, ExamStu
from project.views import ar_time, send_note, to_hijri
from sheikhs.models import Sheikh
from students.models import Student
from students.views import count_progress
from .forms import EditRwiaShikh, EditShikhProfile, StuExamQue, StuExamRes
from django.forms import modelformset_factory
from datetime import date , datetime
import pytz
from django.http import JsonResponse


today = timezone.now() 





@login_required
def sheikh_dash(request):
    sheikh = request.user.sheikh_User
    stu_num = Student.objects.filter(sheikh=sheikh).count()
    need_help_num = Student.objects.filter(sheikh= sheikh, status='need_help').count()
    complete_exam_num = ExamRes.objects.filter(date__date__sheikh=sheikh, score__gt=0).count()
    average_score = ExamRes.objects.filter(date__date__sheikh=sheikh, score__gt=0).aggregate(Avg('score'))['score__avg']

    next_sheikh_dates = ExamDate.objects.filter(sheikh= sheikh, tarkh__gte=today).all()
    if next_sheikh_dates:
        for date in next_sheikh_dates:
            date.hijri = to_hijri(date.tarkh)
            date.from_hour = ar_time(date.from_hour)
            date.to_hour = ar_time(date.to_hour)
            num_book_stu = ExamStu.objects.filter(date=date).count()
            date.remain = date.student_num - num_book_stu
    context = {
        'sheikh': sheikh,
        'next_sheikh_dates':next_sheikh_dates,
        'stu_num':stu_num,
        'need_help_num': need_help_num,
        'complete_exam':complete_exam_num,
        'average_score': round(average_score, 2) if average_score else 0,
    }
    return render(request, 'sheikhs/html/sheikh_dash.html', context)



@login_required
def prev_exam(request):
    sheikh = request.user.sheikh_User
    prev_sheikh_dates = ExamDate.objects.filter(sheikh= sheikh, tarkh__lt=today).order_by("-tarkh")
    if prev_sheikh_dates:
        for date in prev_sheikh_dates:
            date.hijri = to_hijri(date.tarkh)
            date.from_hour = ar_time(date.from_hour)
            date.to_hour = ar_time(date.to_hour)
            num_book_stu = ExamStu.objects.filter(date=date).count()
            date.remain = date.student_num - num_book_stu
    context = {
        'sheikh': sheikh,
        'next_sheikh_dates':prev_sheikh_dates,
    }
    return render(request, 'sheikhs/html/prev_exam.html', context)



@login_required
def view_date(request, id):
    dates = ExamStu.objects.filter(date__id = id, date__sheikh = request.user.sheikh_User).all()
    if dates:
        for date in dates: 
            dates.hijry = to_hijri(date.date.tarkh)
            date.status = dict({"active": "نشط", 
                                "need_help": "محتاج متابعة", 
                                "withdrawn": "منسحب", 
                                "graduated": "متخرج", 
                                "excluded": "معتذر مؤقتا"}).get(date.student.status)
            date.track = dict({"track_1": "المساق الأول", 
                           "track_2": "المساق الثاني", 
                           "track_3": "المساق الثالث"}).get(date.student.track.name)
    else:
        dates.hijry = to_hijri(ExamDate.objects.filter(id= id).first().tarkh)
        
    context ={
        'dates': dates,
    }
    return render(request, 'sheikhs/html/date_stu.html',context)

@login_required
def com_exam(request):
    dates = ExamRes.objects.filter(date__date__sheikh= request.user.sheikh_User, score__gt= 0, date__date__tarkh__lt=today).order_by("-date__date__tarkh")
    for date in dates:
        date.hijri = to_hijri(date.date.date.tarkh)
        date.from_hour = ar_time(date.date.date.from_hour)
        date.to_hour = ar_time(date.date.date.to_hour)
        date.memorization_level = dict(ExamRes._meta.get_field('memorization_level').choices).get(date.memorization_level)
        date.tajweed_level = dict(ExamRes._meta.get_field('tajweed_level').choices).get(date.tajweed_level)
    query = request.GET.get('q', '')
    
    if query:
        results = ExamRes.objects.filter(date__date__sheikh = request.user.sheikh_User, score__gt= 0, date__date__tarkh__lt=today ,student__user__name__icontains = query).all()
        data = {
            "results": [{"name": p.student.user.name,
                         "date": to_hijri(p.date.date.tarkh) , 
                         "score": p.score, 
                         "memorization_level": dict(ExamRes._meta.get_field("memorization_level").choices).get(p.memorization_level), 
                         "tajweed_level": dict(ExamRes._meta.get_field("memorization_level").choices).get(p.tajweed_level),
                         "id": date.date.id,
                         "code": date.student.user.code,
                         } for p in results]
        }
        return JsonResponse(data)


    context ={
        'dates': dates
    }
    return render(request, 'sheikhs/html/com_exam.html',context)


@login_required
def stu_res(request,date_id ,stu_code):
    student = get_object_or_404(Student, user__code= stu_code)
    date_stu = get_object_or_404(ExamStu, id= date_id, student= student)
    
    prev_res = ExamRes.objects.filter(date= date_stu, date__student= student).first()
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

        
    print(stu_que_form)
    context ={
        'student': student,
        'date_stu': to_hijri(date_stu.date.tarkh),
        'stu_res_form':stu_res_form,
        'num_ques': num_ques,
        'stu_que_form':stu_que_form,
    }
    return render(request, 'sheikhs/html/stu_res.html',context)


@login_required
def dateView(request, date_id):
    result = ExamStu.objects.filter(id=date_id).first()
    exam = ExamRes.objects.filter(date=result).first()
    degree = ExamQuestion.objects.filter(exam= exam)   
    exam.percentage = int((exam.score / 20) *100) or "-"
    exam.memorization_level = dict({"excellent": "ممتاز", "very_good": " جيد جدا", "good": "جيد", "fair": "مقبول", "weak": "ضعيف"}).get(exam.memorization_level) or "-"
    exam.tajweed_level = dict({"excellent": "ممتاز", "very_good": " جيد جدا", "good": "جيد", "fair": "مقبول", "weak": "ضعيف"}).get(exam.tajweed_level) or "-"
    exam.notes = exam.notes or "-"
    exam.hijriDate = to_hijri(exam.date.date.tarkh)
   
    context = {
        'exam': exam,
        'degree': degree,
    }
    return render(request, 'sheikhs/html/date_view.html', context)

@login_required
def my_stu(request):
    sheikh = request.user.sheikh_User
    if sheikh:
        students = Student.objects.filter(sheikh=sheikh)
        
    else:
        return redirect('/dash')
    context = {
        'students': students,

    }
    return render(request, 'sheikhs/html/my_stu.html', context)



@login_required
def need_help_stu(request):
    sheikh = request.user.sheikh_User
    if sheikh:
        students = Student.objects.filter(sheikh=sheikh, status='need_help').all()
        for stu in students:
            try:
                stu.last_exam = ExamRes.objects.filter(date__student=stu).last()
            except:
                pass
    else:
        return redirect('/dash')
    context = {
        'students': students,

    }
    return render(request, 'sheikhs/html/need_help_stu.html', context)




@login_required
def stu_dash(request, stu_code):
    student = Student.objects.filter(user__code=stu_code).first()
    student.status = dict({"active": "نشط", 
                                "need_help": "محتاج متابعة", 
                                "withdrawn": "منسحب", 
                                "graduated": "متخرج", 
                                "excluded": "معتذر مؤقتا"}).get(student.status)
    student.progress = count_progress(student.track.name, student.nsap)
    next = ExamStu.objects.filter(student=student, date__tarkh__gt=today).first()
    student.nextExam= to_hijri(next.date.tarkh) if next else "لا يوجد"
    
    exam_log = ExamStu.objects.filter(student=student)
    for exam in exam_log:
        result = ExamRes.objects.filter(date=exam).first()
        if result and result.score != 0:
            exam.percentage = int((result.score / 20) *100)
            exam.memorization_level = dict(ExamRes._meta.get_field('memorization_level').choices).get(result.memorization_level)
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
    return render(request, 'sheikhs/html/stu_dash.html', context)


@login_required
def profile(request):
    sheikh = request.user.sheikh_User
    if sheikh:
        sheikh.hijri = to_hijri(sheikh.user.birth)
        sheikh.rwia = dict(Sheikh._meta.get_field('rwia').choices).get(sheikh.rwia)
        sheikh.country = dict(User._meta.get_field('country').choices).get(sheikh.user.country)
    else:
        return redirect('/dash')
    
    
    context = {
        'sheikh': sheikh,

    }
    
    return render(request, 'sheikhs/html/profile.html', context)



@login_required
def edit_profile(request):
    if request.method == 'POST':
        edit_profile_form = EditShikhProfile(request.POST, instance=request.user)
        edit_rwia_form = EditRwiaShikh(request.POST, instance=request.user.sheikh_User)
        if edit_profile_form.is_valid() and edit_rwia_form.is_valid():
            edit_profile_form.save()
            edit_rwia_form.save()
            messages.success(request, "تم تعديل البيانات بنجاح ✅")
            return redirect('/dash') 
        else:
            messages.error(request, "حدث خطأ أثناء تعديل البيانات ❌")
            

    else:
        edit_profile_form = EditShikhProfile(instance=request.user)
        edit_rwia_form = EditRwiaShikh(instance=request.user.sheikh_User)
        
    context = {
        'edit_profile_form': edit_profile_form,
        'edit_rwia_form': edit_rwia_form,
    }
    
    return render(request, 'sheikhs/html/edit_profile.html', context)




