from django.urls import path
from . import views

urlpatterns = [
    path('users/create/', views.create_user, name='create_user'),
    path('users/<int:user_id>/', views.get_user, name='get_user'),
    path('expenses/create/', views.create_expense, name='create_expense'),
    path('expenses/<int:expense_id>/', views.get_expense, name='get_expense'),
    path('users/<int:user_id>/expenses/', views.get_user_expenses, name='get_user_expenses'),
    path('expenses/', views.get_overall_expenses, name='get_overall_expenses'),
    path('balance-sheet/', views.download_balance_sheet, name='download_balance_sheet'),
    path('balance-details/', views.get_balance_details, name='get_balance_details'),
]