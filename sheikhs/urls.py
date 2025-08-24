from django.urls import path
from .views import *


urlpatterns = [
    path('', sheikh_dash),
    path('profile', profile),
    path('editprofile', edit_profile),
    path('my_stu', my_stu),
    path('need_help', need_help_stu),
    path('com_exam/', com_exam),
    path('prev_exam', prev_exam),
    path('date/<int:id>', view_date),
    path('date/<int:date_id>/<str:stu_code>', stu_res),
    path('date_view/<int:date_id>', dateView),
    path('my_stu/<str:stu_code>', stu_dash),
]
