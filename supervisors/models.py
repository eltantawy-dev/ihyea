from django.db import models
from django.conf import settings
from followups.models import FollowUpSupervisor




class Supervisor(models.Model):
    STATUS_CHOICES = [
        ('active', 'نشط'),
        ('need_help', 'يحتاج متابعة'),
        ('excused', 'معتذر مؤقتا'),
        ('withdrawn', 'منسحب'),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=("حساب المشرف"), related_name='supervisor_User')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='الحالة')
    followup_supervisor = models.ForeignKey(FollowUpSupervisor, on_delete=models.SET_NULL, verbose_name='مشرف المتابعة', null=True, blank=True, related_name='supervisors')

    def __str__(self):
        return f"{self.user.name} - مشرف"
    
    class Meta:
        verbose_name = 'مشرف'           
        verbose_name_plural = 'المشرفون'   

