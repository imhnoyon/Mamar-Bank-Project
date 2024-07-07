from django.urls import path
from . import views
urlpatterns = [
    path('register/',views.RegistrationForm.as_view(),name='register'),
    path('login/',views.userLoginView.as_view(),name='login'),
    path('logout/',views.userLogoutView.as_view(),name='logout'),
    path('profile/',views.UserBankAccountUpdateView.as_view(),name='profile'),
]