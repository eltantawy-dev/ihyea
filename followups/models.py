from django.conf import settings
from django.db import models

# Create your models here.




class FollowUpSupervisor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=("حساب مشرف المتابعة"), limit_choices_to={'role': 'followup'})
    
    def __str__(self):
        return f"{self.user.name} - مشرف متابعة"
    
    class Meta:
        verbose_name = 'مشرف متابعة'           
        verbose_name_plural = 'مشرفوا المتابعة'   