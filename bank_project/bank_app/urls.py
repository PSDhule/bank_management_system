from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),

    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password,
    name='change_password'),

    path('deposit/', views.deposit, name='deposit'),
    path('withdraw/', views.withdraw, name='withdraw'),
    path('transfer/', views.transfer_money, name='transfer'),

    path('transactions/', views.transactions, name='transactions'),

    # RECEIPT
    path(
        'receipt/<int:transaction_id>/',
        views.receipt,
        name='receipt'
    ),

    # ADMIN
    path(
        'admin-dashboard/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),

    path(
        'admin-customers/',
        views.admin_customers,
        name='admin_customers'
    ),

    path(
        'admin-accounts/',
        views.admin_accounts,
        name='admin_accounts'
    ),

    path(
        'admin-transactions/',
        views.admin_transactions,
        name='admin_transactions'
    ),

    # CUSTOMERS
    path(
        'customers/',
        views.customers,
        name='customers'
    ),

    path(
        'customers/<int:customer_id>/',
        views.customer_detail,
        name='customer_detail'
    ),

    path('logout/', views.logout_view, name='logout'),
]