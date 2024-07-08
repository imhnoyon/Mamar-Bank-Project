from django import forms
from django.db.models.query import QuerySet
from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import CreateView,ListView,View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Transactions
from .forms import DepositForm,WithdrawForm,LoanRequestForm
from .constrants import DEPOSIT,WITHDRAWAL,LOAN,LOAN_PAID,SENT_MONEY,RECEIVED_MONEY
from django.contrib import messages
from datetime import datetime
from django.db.models import Sum
from django.urls import reverse_lazy
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from .forms import TransactionForms
from accounts.models import UserBankAccount,Bankrupt
from django.core.mail import EmailMessage,EmailMultiAlternatives
from django.template.loader import render_to_string
from django.http import HttpResponse

# Create your views here.

def send_transaction_email(user, amount, subject, template):
        message = render_to_string(template, {
            'user' : user,
            'amount' : amount,
        })
        send_email = EmailMultiAlternatives(subject, '', to=[user.email])
        send_email.attach_alternative(message, "text/html")
        send_email.send()

class CreateTransactionView(LoginRequiredMixin, CreateView):
    template_name = 'transactions/transaction_form.html'
    model = Transactions
    title = ''
    success_url = reverse_lazy('transaction_report')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account,
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title
        })
        return context


class DepositMoneyView(CreateTransactionView):
    form_class=DepositForm
    title='Deposit'
    def get_initial(self):
        initial={'transaction_type':DEPOSIT}
        return initial
    
    def form_valid(self, form):
        amount=form.cleaned_data.get('amount')
        account=self.request.user.account
        account.balance +=amount
        account.save(
            update_fields=['balance']
        )

        messages.success(self.request,f"{amount}$ was diposited to your account successfully")
        send_transaction_email(self.request.user, amount, "Deposit Message", "transactions/deposit_email.html")
        return super().form_valid(form)
    



class WithdrawView(CreateTransactionView):
    form_class=WithdrawForm
    title='Withdraw Money'

    def get_initial(self):
        initial={'transaction_type':WITHDRAWAL}
        return initial
    def form_valid(self,form):
        amount=form.cleaned_data.get('amount')
        account=self.request.user.account
        result=Bankrupt.objects.all().first()
        if result.bankrupt==False:
            account.balance -=amount
            account.save(
                update_fields=['balance']
            )
            messages.success(self.request,f"Successfully withdrawn {amount}$ from your account successfully")
            send_transaction_email(self.request.user, amount, "Withdraw Message", "transactions/withdraw_email.html")
            return super().form_valid(form)
        else:
            messages.error(self.request,"Don't withdraw amount baceause bank is bankrupt")
            return self.form_invalid(form)


class LoanRequestView(CreateTransactionView):
    form_class=LoanRequestForm
    title='Request For Loan'
    def get_initial(self):
        initial={'transaction_type':LOAN}
        return initial
    def form_valid(self,form):
        amount=form.cleaned_data.get('amount')
        current_loan_count=Transactions.objects.filter(account=self.request.user.account,transaction_type=3,loan_approve=True).count()
        result=Bankrupt.objects.all().first()
        if result.bankrupt==False:
            if current_loan_count >=3:
                return HttpResponse("You have crossed Your limits")
            messages.success(self.request,f"Loan request for amount {amount} $ has been successfully sent to admin")
            send_transaction_email(self.request.user, amount, "Loan Request ", "transactions/loan_request_for_manager.html")
            return super().form_valid(form)
        else:
            messages.error(self.request,"Bank is bankrupt")
            return self.form_invalid(form)




class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = 'transactions/transaction_report.html'
    model = Transactions
    balance = 0 
    context_object_name = 'report_list' 
    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account=self.request.user.account
        )
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            queryset = queryset.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)
            self.balance = Transactions.objects.filter(
                timestamp__date__gte=start_date, timestamp__date__lte=end_date
            ).aggregate(Sum('amount'))['amount__sum']
        else:
            self.balance = self.request.user.account.balance
       
        return queryset.distinct() 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account
        })

        return context



class PayLoanView(LoginRequiredMixin, View):
    
    def get(self, request, loan_id):
        loan = get_object_or_404(Transactions, id=loan_id)
        if loan.loan_approve:
            user_account = loan.account
            if loan.amount < user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.loan_approve = True
                loan.transaction_type = LOAN_PAID
                loan.save()
                return redirect('loans_list')
            else:
                messages.error(
            self.request,f'Loan amount is greater than available balance'
        )

        return redirect('pay')
        
    



class LoanListView(LoginRequiredMixin,ListView):
    model = Transactions
    template_name = 'transactions/loan_request.html'
    context_object_name = 'loans' 
    
    def get_queryset(self):
        user_account = self.request.user.account
        queryset = Transactions.objects.filter(account=user_account,transaction_type=3)
        
        return queryset






class TransferView(FormView):
    template_name = 'transactions/transfer.html'
    form_class = TransactionForms
    success_url = reverse_lazy('transaction_report')  

    def form_valid(self, form):
        account_number = form.cleaned_data['account_number']
        amount = form.cleaned_data['amount']
        
        user_account = self.request.user.account
        
        if amount > user_account.balance:
            messages.error(self.request, 'Transfer amount is greater than available balance.')
            return redirect('transfer')  
        
        recipient_account = UserBankAccount.objects.filter(account_No=account_number).first()
        if not recipient_account:
            messages.error(self.request, 'Recipient account not found.')
            return redirect('transfer') 
        
        recipient_account.balance += amount
        user_account.balance -= amount
        recipient_account.save()
        user_account.save()
        Transaction_sender=Transactions(
              account=user_account,
              transaction_type=SENT_MONEY,
              amount=amount,
              balance_after_transaction=user_account.balance
         )
        Transaction_sender.save()

        Transaction_reciver=Transactions(
              account=recipient_account,
              transaction_type=RECEIVED_MONEY,
              amount=amount,
              balance_after_transaction=recipient_account.balance
         )
        Transaction_reciver.save()

        messages.success(self.request, 'Transfer successful.')
        send_transaction_email(self.request.user, amount, "Transfer", "transactions/transfer_messages.html")

        send_transaction_email(recipient_account.user, amount, "Received", "transactions/received_email.html")

        
        return super().form_valid(form)
    
    
def Bank(request):
    result=Bankrupt.objects.all()
    for i in result:
        print(i)

    return render(request,'bankrupt.html')




