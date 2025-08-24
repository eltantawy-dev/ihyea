from django.db import models
from django.conf import settings
from sheikhs.models import Sheikh
from tracks.models import *


class Student(models.Model):
    
    STATUS_CHOICES = [
        ('active', 'نشط'),
        ('need_help', 'محتاج متابعة'),
        ('excluded', 'مستبعد'),
        ('withdrawn', 'منسحب'),
        ('graduated', 'متخرج'),
    ]
    
    RWIA_CHOICES = [
        ('hfs', 'حفص'),
        ('wrsh', 'ورش'),
        ('qalon', 'قالون'),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=("حساب الطالب"), on_delete=models.CASCADE ,limit_choices_to={'role': 'student'}, related_name='student_User')
    sheikh = models.ForeignKey(Sheikh, on_delete=models.SET_NULL, null=True, blank=True, related_name='students', verbose_name='الشيخ')
    rwia = models.CharField(max_length=15, choices=RWIA_CHOICES, verbose_name='الرواية')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='الحالة')
    track = models.ForeignKey(Track, on_delete=models.DO_NOTHING, verbose_name='المساق')
    nsap = models.PositiveIntegerField(null=True, blank=True,verbose_name='المحفوظ')
    
    
    def __str__(self):
        rwia_display = dict(self.RWIA_CHOICES).get(self.rwia, self.rwia)
        return f"{self.user.name} - {self.track} - {rwia_display}"
    
    class Meta:
        verbose_name = 'طالب'           
        verbose_name_plural = 'الطلاب'   



class Notes(models.Model):
    user = models.ForeignKey(Student, verbose_name=("الطالب"), on_delete=models.CASCADE, limit_choices_to={'user': True})
    title = models.CharField(verbose_name=("العنوان"), max_length=150)
    message = models.CharField(verbose_name=("الرسالة"), max_length=400)
    is_read = models.BooleanField(verbose_name=("مقروء"), default= False)
    created_at = models.DateTimeField(verbose_name=("التاريخ"), auto_now_add=True)
    
    def __str__(self):
        return f" إشعار ل: {self.user.user.name} بعنوان {self.title}"
    
    class Meta:
        verbose_name = 'إشعار'           
        verbose_name_plural = 'الإشعارات'





EXCUSE_CHOICES = [
    ('sick', 'مرض'),
    ('death', 'حالة وفاة'),
    ('work', 'ظروف العمل'),
    ('study', 'ظروف دراسية'),
    ('power', 'انقطاع الكهرباء'),
    ('other', 'أخرى'),
]
STATUS_CHOICES = [
    ('on', 'تحت المراجعة'),
    ('rejected', 'مرفوض'),
    ('ok', 'مقبول'),
]

class Excuse(models.Model):
    user = models.ForeignKey(Student, verbose_name=("الطالب"), on_delete=models.CASCADE)
    type_excuse = models.CharField(verbose_name='نوع العذر', choices=EXCUSE_CHOICES , max_length=100)
    message = models.CharField(verbose_name= 'الرسالة',max_length=2000)
    status = models.CharField(verbose_name="الحالة",choices=STATUS_CHOICES ,max_length=50, default="on")
    
    def __str__(self):
        return f" عذر الطالب: {self.user.user.name}"
    
    class Meta:
        verbose_name = 'عذر'           
        verbose_name_plural = 'الأعذار'

