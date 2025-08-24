from django.db import models
from accounts.models import *
from sheikhs.models import Sheikh
from tracks.models import *
from students.models import Student
from hijri_converter import Gregorian # type: ignore


DAYS_AR = {
                    'Saturday': 'السبت',
                    'Sunday': 'الأحد',
                    'Monday': 'الإثنين',
                    'Tuesday': 'الثلاثاء',
                    'Wednesday': 'الأربعاء',
                    'Thursday': 'الخميس',
                    'Friday': 'الجمعة',
                }


class ExamDate(models.Model):
    sheikh = models.ForeignKey(Sheikh, verbose_name=("الشيخ"), on_delete=models.CASCADE)
    tarkh = models.DateField(verbose_name=("التاريخ"), auto_now=False, auto_now_add=False)
    from_hour = models.TimeField(verbose_name=("من الساعة"), auto_now=False, auto_now_add=False)
    to_hour = models.TimeField(verbose_name=("إلى الساعة"), auto_now=False, auto_now_add=False)
    student_num = models.PositiveIntegerField(verbose_name=("عدد الطلاب"))
    
    def __str__(self):
        day_name_en = self.tarkh.strftime('%A')
        day_name_ar = DAYS_AR.get(day_name_en, '')
        hijri_date = Gregorian(self.tarkh.year, self.tarkh.month, self.tarkh.day).to_hijri()
        next_exam = f"موعد الشيخ {self.sheikh.user.name} || {self.from_hour.hour}:{self.from_hour.minute} - {self.to_hour.hour}:{self.to_hour.minute} ـ {day_name_ar} {hijri_date.day}/{hijri_date.month}/{hijri_date.year} هـ"
        return next_exam
    
    class Meta:
        verbose_name = 'اختبار'           
        verbose_name_plural = 'الاختبارات'


class ExamStu(models.Model):
    date = models.ForeignKey(ExamDate, verbose_name=("الموعد"), on_delete=models.CASCADE)
    student = models.ForeignKey(Student, verbose_name=("الطالب"), on_delete=models.CASCADE)
    nsap = models.PositiveIntegerField(verbose_name=("النصاب"), default=0)
    stage = models.ForeignKey(Stage, verbose_name=("المرحلة"), on_delete=models.DO_NOTHING)
    attempt_number = models.PositiveIntegerField(default=1, verbose_name=("رقم المحاولة"))
    book_date = models.DateTimeField(auto_now=True, verbose_name=("تاريخ الحجز"))
    
    def __str__(self):
        return f"الطالب: {self.student} || الموعد: {self.date}"
    
    class Meta:
        verbose_name = 'طالب باختبار'           
        verbose_name_plural = 'طلاب الاختبارات'

    
class ExamRes(models.Model):
    date = models.ForeignKey(ExamStu, verbose_name=("الموعد"), on_delete=models.CASCADE, related_name='exam_res')
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name=("الدرجة"))
    status = models.CharField(max_length=50, choices=[
        ('passed', 'ناجح'),
        ('Failed', 'راسب'),
    ], verbose_name=("الحالة"), null=True, blank=True,)
    memorization_level = models.CharField(max_length=50, choices=[
        ('excellent', 'ممتاز'),
        ('very_good', 'جيد جدا'),
        ('good', 'جيد'),
        ('fair', 'مقبول'),
        ('weak', 'ضعيف'),
    ], verbose_name=("تقدير الحفظ"))
    tajweed_level = models.CharField(max_length=50, choices=[
        ('excellent', 'ممتاز'),
        ('very_good', 'جيد جدا'),
        ('good', 'جيد'),
        ('fair', 'مقبول'),
        ('weak', 'ضعيف'),
    ], verbose_name=("تقدير التجويد"))
    notes = models.TextField(verbose_name=("الملاحظات"))
    
    def __str__(self):
        return f"نتيجة الطالب {self.date.student} - {self.date.stage} "
    
    class Meta:
        verbose_name = 'تقييم اختبار'           
        verbose_name_plural = 'تقييمات الاختبارات'   
    
    

class ExamQuestion(models.Model):
    exam = models.ForeignKey(ExamRes, on_delete=models.CASCADE, related_name='questions', verbose_name=("الاختبار"))
    question_number = models.PositiveIntegerField(verbose_name=("رقم السؤال")) 
    alarm_count = models.PositiveIntegerField(default=0, verbose_name=("عدد التنبيهات")) 
    mistake_count = models.PositiveIntegerField(default=0, verbose_name=("عدد الأخطاء"))  

    def calculate_score(self):
        return max(0, 10 - (self.mistake_count * 1 + self.alarm_count * 0.25))

    def __str__(self):
        return f"سؤال {self.question_number} - اختبار {self.exam}"
    
    class Meta:
        verbose_name = 'درجة سؤال'           
        verbose_name_plural = 'درجات الأسئلة'   




def calc_score(exam_res):
    questions = ExamQuestion.objects.filter(exam=exam_res)
    total_score = sum([question.calculate_score() for question in questions])
    exam_res.score = total_score
    exam_res.save()
    return total_score



def calculate_score(self):
    max_score = 20
    penalty = (self.mistake_count * 1) + (self.alarm_count * 0.25)
    score = max(0, max_score - penalty)
    return score
