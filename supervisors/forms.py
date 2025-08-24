from django import forms
from accounts.models import User
from exams.models import ExamDate, ExamQuestion, ExamRes



class EditProfile(forms.ModelForm):
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
        

class AddDate(forms.ModelForm):
    class Meta:
        model = ExamDate
        fields = ['tarkh','from_hour','to_hour','student_num']
        labels = {
            'tarkh': 'التاريخ',
            'from_hour': 'من الساعة',
            'to_hour': 'إلى الساعة',
            'student_num': 'عدد الطلاب',
        }
        widgets = {
            'tarkh': forms.DateInput(attrs={'type': 'date', 'id': 'hijri-datepicker'}),
            'from_hour': forms.TimeInput(attrs={'type': 'time'}),
            'to_hour': forms.TimeInput(attrs={'type': 'time'}),
        }