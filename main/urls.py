from django.urls import path

from .views import *

app_name = 'main'

urlpatterns = [
    path('', index, name='index'),
    path('accounts/register/activate/<str:sign>/', user_activate, name='register_activate'),
    path('accounts/register/done/', RegisterDoneView.as_view(), name='register_done'),
    path('accounts/register/', RegisterUserView.as_view(), name='register'),
    path('accounts/login/', MBLoginView.as_view(), name='login'),
    path('accounts/profile/change/', ChangeUserInfoView.as_view(), name='profile_change'),
    path('accounts/profile/', profile, name='profile'),
    path('accounts/logout/', MBLogoutView.as_view(), name='logout'),
    path('accounts/password/change/', MBPaswordChangeView.as_view(), name='password_change')


]
