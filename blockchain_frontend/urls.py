"""blockchain_frontend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path
from django.contrib.auth.decorators import login_required

from blockchain_frontend import views as main
from tender import views as tender
from medical_story import views as medical
from login import views as login
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_required(main.prehome), name='prehome'),

    # Tender paths
    path('open_tendering', login_required(tender.open_tendering), name='open-tendering'),
    path('tender', login_required(tender.index), name='index-tender'),

    # Medical Story
    path('medical', login_required(medical.index), name='index-medical'),
    path('medicine', login_required(medical.medicine_index), name='index-medicine'),
    path('patient', login_required(medical.patient_index), name='index-patient'),
    path('history', login_required(medical.history_index), name='index-history'),

    # Account
    path('login', login.index_login, name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('registration', login.registration, name='registration')
]
