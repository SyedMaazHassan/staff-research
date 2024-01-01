from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('fetch-staff', views.fetch_staff_view, name='fetch-staff'),
    path('report/<str:request_id>', views.single_report_view, name='single-report'),
    path('export-report/<str:request_id>', views.ExportCSVView.as_view(), name='export-report'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
