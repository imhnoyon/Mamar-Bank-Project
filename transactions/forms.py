from typing import Any
from django import forms
from .models import Transactions
from accounts.models import UserBankAccount

class TransactionForm(forms.ModelForm):
   
    class Meta:
        model=Transactions
        fields=['amount','transaction_type']
    def __init__(self,*args, **kwargs):
        self.account=kwargs.pop('account')
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled=True
        self.fields['transaction_type'].widget=forms.HiddenInput()

    def save(self, commit=True):
        self.instance.account=self.account
        self.instance.balance_after_transaction=self.account.balance 
        return super().save()
    


class DepositForm(TransactionForm):
    def clean_amount(self): # amount field ke filter korbo
        min_deposit_amount = 500
        amount = self.cleaned_data.get('amount') 
        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f'You need to deposit at least {min_deposit_amount} $'
            )

        return amount
    

class WithdrawForm(TransactionForm):
    def clean_amount(self):
        account=self.account
        min_withdraw_amount=500
        max_withdraw_amount=50000
        balance=account.balance
        amount=self.cleaned_data.get('amount')

        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f"You can withdraw at least {min_withdraw_amount} Taka"
            )
        if amount > max_withdraw_amount:
            raise forms.ValidationError(
                f"You can withdraw at most {min_withdraw_amount} Taka"
            )
        if amount > balance:
            raise forms.ValidationError(
              f"You have {balance} $ in your account"    
              f"You can't not withdraw more than your account balance"
            )
        return amount
    


class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        amount=self.cleaned_data.get('amount')

        return amount




class TransactionForms(forms.Form):
    account_number = forms.CharField(label='Account Number')
    amount = forms.DecimalField(label='Amount')

    def clean(self):
        cleaned_data=super().clean()
        account_number=cleaned_data['account_number']
        amount=cleaned_data['amount']

        user_account=UserBankAccount.objects.filter(account_No=account_number).first()
        if user_account ==None:
            raise forms.ValidationError('Account Not found')

    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class':(
                     'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                )
            })