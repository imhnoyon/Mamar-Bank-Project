from django.urls import path
from .views import DepositMoneyView,WithdrawView,LoanRequestView,PayLoanView,TransactionReportView,LoanListView,TransferView,Bank

urlpatterns = [
    path('deposit/',DepositMoneyView.as_view(),name='deposit_money'),
    path('report/',TransactionReportView.as_view(),name='transaction_report'),
    path('withdraw/',WithdrawView.as_view(),name='withdraw_money'),
    path('loan_request/',LoanRequestView.as_view(),name='loan_request'),
    path('loans/',LoanListView.as_view(),name='loans_list'),
    path('loan/<int:loan_id>/',PayLoanView.as_view(),name='pay'),
    path('transfer/',TransferView.as_view(),name='transfer'),
    path('bankrupt/',Bank,name='bankrupt'),

  
]
