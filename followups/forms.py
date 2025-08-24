from django import forms
from accounts.models import User
from exams.models import ExamDate
from sheikhs.models import Sheikh
from students.models import Student
from supervisors.models import Supervisor

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
        
        
class AddStudent(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['user', 'sheikh']
        labels = {
            'user': 'الطالب',
            'sheikh': 'الشيخ',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        self.fields['user'].queryset = User.objects.filter(student_User__sheikh__isnull=True, role="student")
        self.fields['user'].label_from_instance = lambda obj: obj.name
        self.fields['sheikh'].queryset = Sheikh.objects.filter(supervisor__followup_supervisor=user)
        self.fields['sheikh'].label_from_instance = lambda obj: obj.user.name
        

     
class AddSheikh(forms.ModelForm):
    class Meta:
        model = Sheikh
        fields = ['user', 'rwia', 'supervisor']
        labels = {
            'user': 'المستخدم',
            'rwia': 'الرواية',
            'supervisor': 'المشرف',
        }
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(role="student")
        self.fields['user'].label_from_instance = lambda obj: obj.name
        self.fields['supervisor'].queryset = Supervisor.objects.filter(followup_supervisor=user)
        self.fields['supervisor'].label_from_instance = lambda obj: obj.user.name
        
        
class AddSupervisor(forms.ModelForm):
    class Meta:
        model = Supervisor
        fields = ['user']
        labels = {
            'user': 'المستخدم',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(role="student")
        self.fields['user'].label_from_instance = lambda obj: obj.name

