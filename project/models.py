from django.db import models

class ContactUs(models.Model):
    name = models.CharField(verbose_name='الاسم', max_length=200)
    email = models.EmailField(verbose_name='البريد الإلكتروني')
    title = models.CharField(verbose_name='العنوان', max_length=200)
    message = models.CharField(verbose_name= 'الرسالة',max_length=2000)
    
    def __str__(self):
        return f"طلب تواصل بعنوان: {self.title}"
    
    class Meta:
        verbose_name = 'طلب تواصل'           
        verbose_name_plural = 'طلبات التواصل'

