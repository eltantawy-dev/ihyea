from django import forms
from accounts.models import User
from exams.models import ExamStu
from students.models import Excuse, Student


class BookDate(forms.ModelForm):
    class Meta:
        model = ExamStu 
        fields = ['date', 'nsap']
        labels = {
            'date': 'اختر موعد',
            'nsap': 'النصاب'
        }
        

class EditProfile(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'country', 'email', 'tele']
        labels = {
            'name': 'الاسم',
            'country': 'الدولة',
            'email': 'البريد الإلكتروني',
            'tele': 'معرف التليجرام',
        }

class ExcuseForm(forms.ModelForm):
    class Meta:
        model = Excuse 
        fields = ['type_excuse', 'message']
        labels = {
            'type_excuse': 'نوع العذر',
            'message': 'الرسالة'
        }