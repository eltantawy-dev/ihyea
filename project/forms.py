from django import forms 
from django.contrib.auth.forms import UserCreationForm
from accounts.models import User
from project.models import ContactUs
from students.models import Student


class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'gender','country', 'birth', 'email', 'tele', 'password1', 'password2']
        labels = {
            'name': 'الاسم',
            'username': 'اسم المستخدم',
            'gender': 'الجنس',
            'country': 'الدولة',
            'birth': 'تاريخ الميلاد',
            'email': 'البريد الإلكتروني',
            'tele': 'معرف التليجرام',
        
            
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = ' أنشأ اسم مستخدم مكون من أحرف إنجليزية ولا يسمح فيه إلا باستخدام تلك الرموز فقط @/./+/-/_'
        self.fields['password1'].label = 'كلمة المرور'
        self.fields['password1'].help_text = ' يجب أن تكون على الأقل 8 أحرف ولا تشبه اسم المستخدم أو البريد وتكون عبارة عن حروف وأرقام'
        self.fields['password2'].label = 'تأكيد كلمة المرور'
        self.fields['password2'].help_text = ''

        
        
class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['rwia', 'track']
        labels = {
            'rwia': 'الرواية',
            'track': 'المساق',
        }
        
        
class ContactUsForm(forms.ModelForm):
    class Meta:
        model = ContactUs 
        fields = ['name', 'email', 'title', 'message']
        labels = {
            'name': 'الاسم',
            'email': 'البريد الإلكتروني',
            'title': 'العنوان',
            'message': 'الرسالة',
        }