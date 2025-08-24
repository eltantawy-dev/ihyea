from django.urls import path
from .views import *

urlpatterns = [
    path('', supervisor_dash, name= 'supervisor_dash'),
    path('profile/', profile, name= 'profile'),
    path('editprofile/', editprofile, name= 'editprofile'),
    path('student_search/', student_search, name= 'student_search'),
    path('stu/<str:code>/', stu_dash, name= 'stu_dash'),
    path('next_exams/', next_exams, name= 'next_exams'),
    path('my_students/', my_students, name= 'my_students'),
    path('com_exam/', com_exam, name= 'com_exam'),
    path('date/<int:date_id>/<str:stu_code>/', stu_res),
    path('not_com_exams/', not_com_exams),
    path('sheikh/<str:sheikh_code>/', sheikh_dash),
    path('sheikh/<str:sheikh_code>/add', add_date),
    path('sheikh/<str:sheikh_code>/<int:date_id>/edit_date', edit_date),
    path('sheikh/<str:sheikh_code>/dates', view_dates),
    path('sheikh/<str:sheikh_code>/date/<int:date_id>', view_date),
    
]
