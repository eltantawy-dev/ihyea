from django import forms

from accounts.models import User
from exams.models import ExamQuestion, ExamRes
from sheikhs.models import Sheikh



class EditShikhProfile(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'country', 'birth', 'email', 'tele']
        labels = {
            'name': 'الاسم',
            'country': 'الدولة',
            'birth': 'تاريخ الميلاد',
            'email': 'البريد الإلكتروني',
            'tele': 'معرف التليجرام',  
        }


class EditRwiaShikh(forms.ModelForm):
    class Meta:
        model = Sheikh
        fields = ['rwia']
        labels = {
            'rwia': 'الرواية',
        }
        
        
        
        
class StuExamRes(forms.ModelForm):
    class Meta:
        model = ExamRes 
        fields = ['memorization_level','tajweed_level','notes']
        labels = {
            'memorization_level':'تقييم الحفظ',
            'tajweed_level':'تقييم التجويد',
            'notes':'الملاحظات',
        }
        
class StuExamQue(forms.ModelForm):
    class Meta:
        model = ExamQuestion
        fields = ['alarm_count','mistake_count']
        labels = {
            'alarm_count': 'عدد التنبيهات',
            'mistake_count': 'عدد الأخطاء',
        }