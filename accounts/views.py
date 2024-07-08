from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.views.generic import FormView
from .forms import UserRegistrationForm,UserUpdateFrom
from django.contrib.auth import login,logout
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView,LogoutView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages


# Create your views here.

class RegistrationForm(FormView):
    template_name='accounts/user_registration.html'
    form_class=UserRegistrationForm
    success_url=reverse_lazy('home')

    def form_valid(self, form):
        # print(form.cleaned_data)
        user=form.save()
        login(self.request,user)
        print(user)
        return super().form_valid(form)
    

class userLoginView(LoginView):
    template_name='accounts/user_login.html'
    def get_success_url(self):
        return reverse_lazy('home')
    
class userLogoutView(LogoutView):
    def get_success_url(self):
        if self.request.user.is_authenticated:
            logout(self.request)
        return reverse_lazy('home')
    


class UserBankAccountUpdateView(LoginRequiredMixin,View):
    template_name = 'accounts/profile.html'

    def get(self, request):
        form = UserUpdateFrom(instance=request.user)
        # print(form)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserUpdateFrom(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the user's profile page
        return render(request, self.template_name, {'form': form})
    


from transactions.views import send_transaction_email
def pass_change(request):
    if request.method=='POST':
       form=PasswordChangeForm(request.user,data=request.POST)
       if form.is_valid():
            update_session_auth_hash(request,form.user)
            form.save()
            send_transaction_email(request.user, '', "Password changes", "accounts/update_pass_email.html")
            messages.success(request,'Password Change Successfully')
            print(form)
            return redirect('home')
           
        
    else:
        form=PasswordChangeForm(user=request.user)
    return render(request,'accounts/pass_change.html',{'form': form})
        



