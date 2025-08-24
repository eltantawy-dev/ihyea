from django.urls import path
from .views import *


urlpatterns = [
    path('', student_dash, name= 'student_dash'),
    path('notifications/mark-read/<int:note_id>/', mark_notification_read, name='mark_notification_read'),
    path('deletedata', deletedata),
    path('exam_log', exam_log),
    path('exam_log/<int:date_id>', dateView),
    path('profile', profile),
    path('editprofile', edit_profile),
    path('excuse', excuse),
]