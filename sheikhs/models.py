from django.conf import settings
from django.db import models
from supervisors.models import Supervisor




class Sheikh(models.Model):
    STATUS_CHOICES = [
        ('active', 'نشط'),
        ('need_help', 'يحتاج متابعة'),
        ('excused', 'معتذر مؤقتا'),
        ('withdrawn', 'منسحب'),
    ]
    RWIA_CHOICES = [
        ('hfs', 'حفص'),
        ('wrsh', 'ورش'),
        ('qalon', 'قالون'),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=("حساب الشيخ"), on_delete=models.CASCADE ,related_name='sheikh_User')
    rwia = models.CharField(max_length=30, choices=RWIA_CHOICES, verbose_name='الرواية')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='الحالة')
    supervisor = models.ForeignKey(Supervisor, on_delete=models.SET_NULL, null=True ,blank=True, related_name='sheikhs', verbose_name='المشرف')
    
    def __str__(self):
        return f"{self.user.name} - {self.rwia} - شيخ"
    class Meta:
        verbose_name = 'شيخ'           
        verbose_name_plural = 'الشيوخ' 
        
          

