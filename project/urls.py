"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from .views import FAQ, home, signup, home_redirect, contact_us 
from students.views import student_dash
from django.conf.urls import handler404, handler500
from django.views.generic import TemplateView

handler404 = 'project.views.custom_404'
handler500 = 'project.views.custom_500'

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('', home, name= 'home'),
    path('select2/', include('django_select2.urls')),
    path('dash/', home_redirect, name= 'home_redirect'),
    path('signup/', signup, name= 'signup'),
    path('student_dash/', include('students.urls')),
    path('sheikh_dash/', include('sheikhs.urls')),
    path('supervisor_dash/', include('supervisors.urls')),
    path('followup_dash/', include('followups.urls')),
    path('FAQ/', FAQ),
    path('contact_us/', contact_us),
    path('logout/', auth_views.LoginView.as_view(next_page ='dash/'), name= 'logout')
]


