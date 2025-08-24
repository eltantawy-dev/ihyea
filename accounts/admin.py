from django.contrib import admin
from .models import *


admin.site.site_header = "معهد إحياء"
admin.site.index_title = "لوحة التحكم"
admin.site.site_title = "معهد إحياء"

admin.site.register(User)

admin.site.register(ExcuseTeleAccounts)



