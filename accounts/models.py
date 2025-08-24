from django.contrib.auth.models import AbstractUser 
from django.db import models
from django.conf import settings


COUNTRY_CHOICES = [
    # الدول العربية
    ('egypt', 'مصر'),
    ('jordan', 'الأردن'),
    ('uae', 'الإمارات'),
    ('bahrain', 'البحرين'),
    ('algeria', 'الجزائر'),
    ('sudan', 'السودان'),
    ('iraq', 'العراق'),
    ('kuwait', 'الكويت'),
    ('morocco', 'المغرب'),
    ('saudi_arabia', 'السعودية'),
    ('tunisia', 'تونس'),
    ('oman', 'عُمان'),
    ('palestine', 'فلسطين'),
    ('qatar', 'قطر'),
    ('lebanon', 'لبنان'),
    ('libya', 'ليبيا'),
    ('mauritania', 'موريتانيا'),
    ('yemen', 'اليمن'),
    ('djibouti', 'جيبوتي'),
    ('comoros', 'جزر القمر'),
    ('somalia', 'الصومال'),
    ('syria', 'سوريا'),

    # الدول الإسلامية غير العربية
    ('turkey', 'تركيا'),
    ('pakistan', 'باكستان'),
    ('iran', 'إيران'),
    ('afghanistan', 'أفغانستان'),
    ('indonesia', 'إندونيسيا'),
    ('malaysia', 'ماليزيا'),
    ('niger', 'النيجر'),
    ('senegal', 'السنغال'),
    ('bangladesh', 'بنغلاديش'),
    ('nigeria', 'نيجيريا'),
    ('mali', 'مالي'),
    ('azerbaijan', 'أذربيجان'),
    ('albania', 'ألبانيا'),
    ('kosovo', 'كوسوفو'),

    # باقي دول العالم
    ('germany', 'ألمانيا'),
    ('usa', 'الولايات المتحدة'),
    ('france', 'فرنسا'),
    ('italy', 'إيطاليا'),
    ('china', 'الصين'),
    ('canada', 'كندا'),
    ('india', 'الهند'),
    ('uk', 'المملكة المتحدة'),
    ('spain', 'إسبانيا'),
    ('russia', 'روسيا'),
    ('brazil', 'البرازيل'),
    ('argentina', 'الأرجنتين'),
    ('australia', 'أستراليا'),
    ('japan', 'اليابان'),
    ('south_korea', 'كوريا الجنوبية'),
]

ROLE_CHOICES = [
        ('student', 'طالب'),
        ('sheikh', 'شيخ'),
        ('supervisor', 'مشرف'),
        ('followup', 'مشرف متابعة'),
        ('admin', 'إداري'),
]

GENDER_CHOICES = [
        ('male', 'ذكر'),
        ('female', 'أنثى'),
    ] 

class User(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="الدور", default="student")
    name = models.CharField(max_length=150, verbose_name='الاسم')
    gender = models.CharField(max_length=50, choices=GENDER_CHOICES, verbose_name='النوع')
    country = models.CharField(choices=COUNTRY_CHOICES, verbose_name="الدولة", max_length=50)
    birth = models.DateField(auto_now=False, auto_now_add=False, verbose_name='تاريخ الميلاد')
    email = models.EmailField(max_length=150, verbose_name="البريد الإلكتروني", unique=True)
    code = models.CharField(verbose_name='كود الحساب', max_length=50, unique=True)
    tele = models.CharField(max_length=20, verbose_name='معرف التليجرام')
    teleid = models.BigIntegerField(null=True, blank=True, verbose_name='حساب التليجرام')
    join_date = models.DateField(auto_now=True, verbose_name='تاريخ التسجيل')


    def __str__(self):
        return f"{self.name} - ({self.get_role_display()})"
    
    class Meta:
        verbose_name = 'مستخدم'           
        verbose_name_plural = 'المستخدمون'    
    


class ExcuseTeleAccounts(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=("حساب مشرف المتابعة"), limit_choices_to={'role': 'followup'})

    def __str__(self):
        return f"مشرف أعذار: {self.user.name}"

    class Meta:
        verbose_name = 'مشرف أعذار'           
        verbose_name_plural = 'مشرفوا الأعذار'   
    



 

    

