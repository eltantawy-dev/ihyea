from django.urls import path
from .views import *

urlpatterns = [
    path('', followup_dash, name='followup_dash'),
    path('profile/', profile, name= 'profile'),
    path('student_search/', student_search, name='student_search'),
    path('student_search/', student_search, name='student_search'),
    path('stu/<str:code>/', stu_dash, name= 'stu_dash'),
    path('next_exams/', next_exams, name= 'next_exams'),
    path('my_students/', my_students, name= 'my_students'),
    path('my_students/add/', my_students_add, name= 'my_students_add'),
    path('my_sheikhs/', my_sheikhs, name= 'my_sheikhs'),
    path('my_sheikhs/add/', my_sheikhs_add, name= 'my_sheikhs_add'),
    path('sheikh/<str:sheikh_code>/', sheikh_dash, name= 'sheikh_dash'),
    path('sheikh/<str:sheikh_code>/date/<int:date_id>', view_date, name= 'sheikh_date'),
    path('my_supervisors/', my_supervisors, name= 'my_supervisors'),
    path('my_supervisors/add/', my_supervisors_add, name= 'my_supervisors_add'),
    path('supervisor/<str:supervisor_code>/', supervisor_dash, name= 'supervisor_dash'),
    path('com_exam/', com_exam, name= 'com_exam'),
    path('not_com_exams/', not_com_exams, name= 'not_com_exams'),
    path('date/<int:date_id>/<str:stu_code>/', stu_res, name= 'stu_res'),
    
]
