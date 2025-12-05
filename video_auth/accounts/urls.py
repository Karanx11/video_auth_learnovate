from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('users/', views.users_list, name='users_list'),
    path('user/<int:user_id>/', views.user_detail, name='user_detail'),
    path('contact/', views.contact_us, name='contact_us'),
]
