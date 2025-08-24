from django.contrib import admin
from .models import Excuse, Student, Notes
# Register your models here.


admin.site.register(Student)
admin.site.register(Notes)
admin.site.register(Excuse)