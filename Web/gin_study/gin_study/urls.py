from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),  # 確保這行存在
    path('analysis/', views.analysis_view, name='analysis'),
    path('emo/', views.emo_view, name='emo'),
    path('analysis/<str:subject>/', views.analysis_subject, name='analysis_subject'),
    path('add_Child/', views.add_child_view, name='add_Child'),

]

