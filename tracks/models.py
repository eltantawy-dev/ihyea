from django.db import models


 
class Batch(models.Model):
    name = models.CharField(max_length=30, verbose_name=("اسم الدفعة"))
    num = models.PositiveIntegerField(verbose_name=("رقم الدفعة"))
    is_open_reg = models.BooleanField(default=False, verbose_name=("فتح التسجيل"))
    
    def __str__(self):
        return f"{self.name} {self.num}"
    
    class Meta:
        verbose_name = 'دفعة'           
        verbose_name_plural = 'الدفعات'   
    
 

class Track(models.Model):
    TRACK_CHOICES = [
        ('track_1', 'المساق الأول'),
        ('track_2', 'المساق الثاني'),
        ('track_3', 'المساق الثالث'),
    ]
    
    name = models.CharField(max_length=100, choices=TRACK_CHOICES, verbose_name=("المساق"))
    batch = models.ForeignKey(Batch, verbose_name=("الدفعة"), on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.get_name_display()} - د {self.batch.num}"
    
    class Meta:
        verbose_name = 'مساق'           
        verbose_name_plural = 'المساقات'   

class Stage(models.Model):
    order = models.IntegerField(verbose_name=("رقم المرحلة"))
    track = models.ForeignKey(Track, verbose_name=("المساق"), on_delete=models.CASCADE, related_name='stages')
    is_active = models.BooleanField(default=False, verbose_name=("فتح الرحلة"))
    num_ques = models.PositiveIntegerField(verbose_name=("عدد الأسئلة"))

    def __str__(self):
        return f"مرحلة {self.order} - {self.track.get_name_display()} - د {self.track.batch.num}"
    
    class Meta:
        verbose_name = 'مرحلة'           
        verbose_name_plural = 'المراحل'   