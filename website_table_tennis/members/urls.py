from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import tournament_schedule_view
from django.conf import settings

urlpatterns = [
    path('', views.home, name='home'),  
    path('tournament-schedule/', tournament_schedule_view, name='tournament_schedule'),
    path('training-schedule/', views.training_schedule, name='training_schedule'),
    path('ranking/', views.ranking, name='ranking'),
    path('documentation/', views.documentation, name='documentation'),
    path('forum/', views.forum, name='forum'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('upload/', views.upload_image, name='upload'),  
    path('upload_image/', views.upload_image, name='upload_image'),  
    path('uploaded_images/', views.uploaded_images, name='uploaded_images'),  
    path('profile/', views.profile, name='profile'), 
    path('my-images/', views.user_uploaded_images, name='user_uploaded_images'),
    path('ranking/details/', views.ranking_details, name='ranking_details'),
    path('join_tournament/', views.join_tournament, name='join_tournament'),
    path('register/', views.registration_view, name='registration'),
    path('payment-notification/', views.payment_notification, name='payment_notification'),
]
