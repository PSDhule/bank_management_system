from django.shortcuts import render, redirect
from django.db.models import Sum
from django.db import transaction as db_transaction
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db.models.functions import TruncMonth
from .models import User, Transaction, Transfer
import uuid
from django.shortcuts import render, get_object_or_404
from .models import User


# =====================================================
# HOME
# =====================================================

def home(request):
    return render(request, 'home.html')


# =====================================================
# LOGIN
# =====================================================

def login_view(request):

    if request.method == "POST":

        email = request.POST.get(
            'email', ''
        ).strip().lower()

        password = request.POST.get(
            'password', ''
        )

        if not email or not password:

            return render(
                request,
                'login.html',
                {
                    'error': 'Please enter email and password.'
                }
            )

        try:

            user = User.objects.get(
                email__iexact=email
            )

        except User.DoesNotExist:

            return render(
                request,
                'login.html',
                {
                    'error': 'Email not registered.'
                }
            )

        # Check hashed password
        password_valid = check_password(
            password,
            user.password
        )

        # Support old plain-text passwords
        if (
            not password_valid
            and user.password == password
        ):

            user.password = make_password(password)
            user.save()

            password_valid = True

        if password_valid:

            # Check account status
            if user.account_status != 'Active':

                return render(
                    request,
                    'login.html',
                    {
                        'error': 'Your account is not active.'
                    }
                )

            # Session
            request.session['user_id'] = user.id
            request.session['user'] = user.name
            request.session['email'] = user.email
            request.session['balance'] = user.balance
            request.session['role'] = user.role

            # Admin
            if user.role == 'admin':
                return redirect('admin_dashboard')

            # Customer
            return redirect('dashboard')

        return render(
            request,
            'login.html',
            {
                'error': 'Wrong password.'
            }
        )

    return render(request, 'login.html')


# =====================================================
# SIGNUP
# =====================================================

def signup(request):

    if request.method == "POST":

        name = request.POST.get(
            'name', ''
        ).strip()

        email = request.POST.get(
            'email', ''
        ).strip().lower()

        password = request.POST.get(
            'password', ''
        )

        confirm_password = request.POST.get(
            'confirm_password', ''
        )

        if (
            not name
            or not email
            or not password
            or not confirm_password
        ):

            messages.error(
                request,
                'Please fill all fields.'
            )

            return redirect('signup')

        if password != confirm_password:

            messages.error(
                request,
                'Passwords do not match.'
            )

            return redirect('signup')

        if len(password) < 6:

            messages.error(
                request,
                'Password must contain at least 6 characters.'
            )

            return redirect('signup')

        if User.objects.filter(
            email__iexact=email
        ).exists():

            messages.error(
                request,
                'Email already registered.'
            )

            return redirect('signup')

        User.objects.create(

            name=name,

            email=email,

            password=make_password(password),

            balance=0,

            role='customer',

            account_status='Active'
        )

        messages.success(
            request,
            'Account created successfully! Please login.'
        )

        return redirect('login')

    return render(request, 'signup.html')


# =====================================================
# CUSTOMER DASHBOARD
# =====================================================

def dashboard(request):

    if 'user_id' not in request.session:
        return redirect('login')

    try:

        user = User.objects.get(
            id=request.session['user_id']
        )

    except User.DoesNotExist:

        request.session.flush()
        return redirect('login')

    # Admin should not access customer dashboard
    if user.role == 'admin':
        return redirect('admin_dashboard')

    # Project Account Number
    account_number = f"SB{user.id:06d}"

    return render(
        request,
        'dashboard.html',
        {
            'user': user.name,
            'balance': user.balance,
            'account_number': account_number,
            'email': user.email,
            'phone': user.phone,
            'address': user.address,
        }
    )


# =====================================================
# PROFILE
# =====================================================

def profile(request):

    if 'user_id' not in request.session:
        return redirect('login')

    try:

        user = User.objects.get(
            id=request.session['user_id']
        )

    except User.DoesNotExist:

        request.session.flush()
        return redirect('login')

    # Project Account Number
    account_number = f"SB{user.id:06d}"

    # Demo IFSC for project
    ifsc_code = "SECB0000001"

    return render(
        request,
        'profile.html',
        {
            'user': user,
            'account_number': account_number,
            'ifsc_code': ifsc_code,
        }
    )


# =====================================================
# EDIT PROFILE
# =====================================================

def edit_profile(request):

    if 'user_id' not in request.session:
        return redirect('login')

    try:
        user = User.objects.get(
            id=request.session['user_id']
        )

    except User.DoesNotExist:
        request.session.flush()
        return redirect('login')

    if request.method == "POST":

        name = request.POST.get(
            'name',
            ''
        ).strip()

        phone = request.POST.get(
            'phone',
            ''
        ).strip()

        address = request.POST.get(
            'address',
            ''
        ).strip()

        if not name:

            return render(
                request,
                'edit_profile.html',
                {
                    'user': user,
                    'error': 'Name is required.'
                }
            )

        user.name = name
        user.phone = phone
        user.address = address

        user.save()

        # Update session name
        request.session['user'] = user.name

        messages.success(
            request,
            'Profile updated successfully.'
        )

        return redirect('profile')

    return render(
        request,
        'edit_profile.html',
        {
            'user': user
        }
    )

# =====================================================
# CHANGE PASSWORD
# =====================================================

# =====================================================
# CHANGE PASSWORD
# =====================================================

def change_password(request):

    if 'user_id' not in request.session:
        return redirect('login')

    try:
        user = User.objects.get(
            id=request.session['user_id']
        )

    except User.DoesNotExist:
        request.session.flush()
        return redirect('login')

    if request.method == "POST":

        current_password = request.POST.get(
            'current_password',
            ''
        )

        new_password = request.POST.get(
            'new_password',
            ''
        )

        confirm_password = request.POST.get(
            'confirm_password',
            ''
        )

        # ==========================================
        # CHECK CURRENT PASSWORD
        # ==========================================

        password_correct = False

        # Check hashed password
        if check_password(
            current_password,
            user.password
        ):
            password_correct = True

        # Check old plaintext password
        elif current_password == user.password:
            password_correct = True

        if not password_correct:

            return render(
                request,
                'change_password.html',
                {
                    'error': 'Current password is incorrect.'
                }
            )

        # ==========================================
        # CHECK NEW PASSWORD
        # ==========================================

        if len(new_password) < 6:

            return render(
                request,
                'change_password.html',
                {
                    'error':
                    'New password must be at least 6 characters.'
                }
            )

        # ==========================================
        # CONFIRM PASSWORD
        # ==========================================

        if new_password != confirm_password:

            return render(
                request,
                'change_password.html',
                {
                    'error':
                    'New password and confirm password do not match.'
                }
            )

        # ==========================================
        # SAVE NEW PASSWORD
        # ==========================================

        user.password = make_password(new_password)

        user.save()

        messages.success(
            request,
            'Password changed successfully.'
        )

        return redirect('profile')

    return render(
        request,
        'change_password.html'
    )

# =====================================================
# DEPOSIT
# =====================================================

def deposit(request):

    if 'user_id' not in request.session:
        return redirect('login')

    try:

        user = User.objects.get(
            id=request.session['user_id']
        )

    except User.DoesNotExist:

        request.session.flush()
        return redirect('login')

    if request.method == "POST":

        try:

            amount = int(
                request.POST.get('amount')
            )

        except (TypeError, ValueError):

            return render(
                request,
                'deposit.html',
                {
                    'error': 'Invalid amount.'
                }
            )

        if amount <= 0:

            return render(
                request,
                'deposit.html',
                {
                    'error': 'Enter a valid amount.'
                }
            )

        user.balance += amount
        user.save()

        request.session['balance'] = user.balance

        Transaction.objects.create(

            user=user,

            type='Deposit',

            amount=amount,

            reference=f"DEP-{uuid.uuid4().hex[:8].upper()}"
        )

        messages.success(
            request,
            f'₹{amount} deposited successfully.'
        )

        return redirect('dashboard')

    return render(
        request,
        'deposit.html'
    )


# =====================================================
# WITHDRAW
# =====================================================

def withdraw(request):

    if 'user_id' not in request.session:
        return redirect('login')

    try:

        user = User.objects.get(
            id=request.session['user_id']
        )

    except User.DoesNotExist:

        request.session.flush()
        return redirect('login')

    if request.method == "POST":

        try:

            amount = int(
                request.POST.get('amount')
            )

        except (TypeError, ValueError):

            return render(
                request,
                'withdraw.html',
                {
                    'error': 'Invalid amount.'
                }
            )

        if amount <= 0:

            return render(
                request,
                'withdraw.html',
                {
                    'error': 'Enter a valid amount.'
                }
            )

        if user.balance < amount:

            return render(
                request,
                'withdraw.html',
                {
                    'error': 'Insufficient balance.'
                }
            )

        user.balance -= amount
        user.save()

        request.session['balance'] = user.balance

        Transaction.objects.create(

            user=user,

            type='Withdraw',

            amount=amount,

            reference=f"WDR-{uuid.uuid4().hex[:8].upper()}"
        )

        messages.success(
            request,
            f'₹{amount} withdrawn successfully.'
        )

        return redirect('dashboard')

    return render(
        request,
        'withdraw.html'
    )


# =====================================================
# TRANSFER MONEY
# =====================================================

def transfer_money(request):

    if 'user_id' not in request.session:
        return redirect('login')

    try:

        sender = User.objects.get(
            id=request.session['user_id']
        )

    except User.DoesNotExist:

        request.session.flush()
        return redirect('login')

    if request.method == "POST":

        receiver_email = request.POST.get(
            'receiver_email',
            ''
        ).strip().lower()

        amount_text = request.POST.get(
            'amount',
            ''
        ).strip()

        if not receiver_email or not amount_text:

            return render(
                request,
                'transfer.html',
                {
                    'error': 'Please fill all required fields.'
                }
            )

        try:

            amount = int(amount_text)

        except ValueError:

            return render(
                request,
                'transfer.html',
                {
                    'error': 'Please enter a valid amount.'
                }
            )

        if amount <= 0:

            return render(
                request,
                'transfer.html',
                {
                    'error': 'Amount must be greater than ₹0.'
                }
            )

        if receiver_email == sender.email.lower():

            return render(
                request,
                'transfer.html',
                {
                    'error':
                    'You cannot transfer money to your own account.'
                }
            )

        try:

            receiver = User.objects.get(
                email__iexact=receiver_email
            )

        except User.DoesNotExist:

            return render(
                request,
                'transfer.html',
                {
                    'error':
                    'Receiver account not found.'
                }
            )

        if receiver.account_status != 'Active':

            return render(
                request,
                'transfer.html',
                {
                    'error':
                    'Receiver account is not active.'
                }
            )

        if sender.balance < amount:

            return render(
                request,
                'transfer.html',
                {
                    'error':
                    'Insufficient balance.'
                }
            )

        reference = (
            f"TRF-{uuid.uuid4().hex[:8].upper()}"
        )

        # Atomic transfer
        with db_transaction.atomic():

            sender.balance -= amount
            sender.save()

            receiver.balance += amount
            receiver.save()

            Transfer.objects.create(

                sender=sender,

                receiver=receiver,

                amount=amount,

                reference=reference,

                status='Completed'
            )

            # Sender transaction
            Transaction.objects.create(

                user=sender,

                type='Transfer',

                amount=amount,

                recipient=receiver.email,

                reference=reference
            )

            # Receiver transaction
            Transaction.objects.create(

                user=receiver,

                type='Transfer',

                amount=amount,

                recipient=sender.email,

                reference=reference
            )

        request.session['balance'] = sender.balance

        messages.success(
            request,
            f'₹{amount} transferred successfully to {receiver.name}.'
        )

        return redirect('dashboard')

    return render(
        request,
        'transfer.html'
    )


# =====================================================
# TRANSACTIONS
# =====================================================

def transactions(request):

    if 'user_id' not in request.session:
        return redirect('login')

    try:
        user = User.objects.get(
            id=request.session['user_id']
        )

    except User.DoesNotExist:
        request.session.flush()
        return redirect('login')

    # All transactions
    data = Transaction.objects.filter(
        user=user
    ).order_by('-date')

    total_deposit = Transaction.objects.filter(
        user=user,
        type='Deposit'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    total_withdraw = Transaction.objects.filter(
        user=user,
        type='Withdraw'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    total_transfer = Transaction.objects.filter(
        user=user,
        type='Transfer'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    return render(
        request,
        'transactions.html',
        {
            'data': data,
            'total_deposit': total_deposit,
            'total_withdraw': total_withdraw,
            'total_transfer': total_transfer,

        }
    )

# =====================================================
# LOGOUT
# =====================================================

def logout_view(request):

    request.session.flush()

    return redirect('home')


# ======== ADMIN DASHBOARD
#==========

def admin_dashboard(request):

    if 'user_id' not in request.session:
        return redirect('login')

    if request.session.get('role') != 'admin':
        return redirect('dashboard')

    # Total customers
    customers = User.objects.filter(
        role='customer'
    ).count()

   # Total accounts
    total_accounts = User.objects.filter(
        role='customer'
    ).count()

    # Total transactions
    total_transactions = Transaction.objects.count()

    # Total bank balance
    total_bank_balance = User.objects.filter(
        role='customer'
    ).aggregate(
        total=Sum('balance')
    )['total'] or 0

    # Total deposits
    total_deposit = Transaction.objects.filter(
        type='Deposit'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    # Total withdraws
    total_withdraw = Transaction.objects.filter(
        type='Withdraw'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    # total transfer
    total_transfer = Transfer.objects.count()

    # Recent transactions
    recent_transactions = Transaction.objects.select_related(
    'user'
    ).order_by('-date')[:10]

    # Monthly transaction statistics
    monthly_transactions = Transaction.objects.annotate(
        month=TruncMonth('date')
    ).values(
        'month'
    ).annotate(
        total=Sum('amount')
    ).order_by('month')

    monthly_deposits = Transaction.objects.filter(
        type='Deposit'
    ).annotate(
        month=TruncMonth('date')
    ).values(
        'month'
    ).annotate(
        total=Sum('amount')
    ).order_by('month')


    monthly_withdrawals = Transaction.objects.filter(
        type='Withdraw'
    ).annotate(
        month=TruncMonth('date')
    ).values(
        'month'
    ).annotate(
        total=Sum('amount')
    ).order_by('month')


    monthly_transfers = Transfer.objects.annotate(
    month=TruncMonth('date')
    ).values(
        'month'
    ).annotate(
        total=Sum('amount')
    ).order_by('month')

    return render(
        request,
        'admin_dashboard.html',
        {
            'customers': customers,
            'total_accounts': total_accounts,
            'total_transactions': total_transactions,
            'total_bank_balance': total_bank_balance,
            'total_deposit': total_deposit,
            'total_withdraw': total_withdraw,
            'total_transfer': total_transfer,
            'recent_transactions': recent_transactions,
            'monthly_transactions': monthly_transactions,
            'monthly_deposits': monthly_deposits,
            'monthly_withdrawals': monthly_withdrawals,
            'monthly_transfers': monthly_transfers,
        }
    )


# ============
# ADMIN CUSTOMERS
# ============

def admin_customers(request):

    if 'user_id' not in request.session:
        return redirect('login')

    if request.session.get('role') != 'admin':
        return redirect('dashboard')

    customers = User.objects.filter(
        role='customer'
    ).order_by('-created_at')

    return render(
        request,
        'admin_customer.html',
        {
            'customers': customers
        }
    )


# =====================================================
# ADMIN ACCOUNTS
# =====================================================

def admin_accounts(request):

    if 'user_id' not in request.session:
        return redirect('login')

    if request.session.get('role') != 'admin':
        return redirect('dashboard')

    accounts = User.objects.filter(
        role='customer'
    ).order_by('-created_at')

    return render(
        request,
        'admin_account.html',
        {
            'accounts': accounts
        }
    )


# =====================================================
# ADMIN TRANSACTIONS
# =====================================================

def admin_transactions(request):

    if 'user_id' not in request.session:
        return redirect('login')

    if request.session.get('role') != 'admin':
        return redirect('dashboard')

    transactions_data = Transaction.objects.select_related(
        'user'
    ).order_by('-date')

    return render(
        request,
        'admin_transation.html',
        {
            'transactions': transactions_data
        }
    )

def customers(request):
    customers = User.objects.all()

    return render(request, 'customers.html', {
        'customers': customers
    })

def customer_detail(request, customer_id):
    customer = User.objects.get(id=customer_id)

    return render(request, 'customer_details.html', {
        'customer': customer
    })

# RECEIPT
def receipt(request, transaction_id):

    if 'user_id' not in request.session:
        return redirect('login')

    try:
        user = User.objects.get(
            id=request.session['user_id']
        )

    except User.DoesNotExist:
        request.session.flush()
        return redirect('login')

    try:
        transaction_data = Transaction.objects.get(
            id=transaction_id,
            user=user
        )

    except Transaction.DoesNotExist:
        messages.error(
            request,
            'Transaction not found.'
        )
        return redirect('transactions')

    account_number = f"SB{user.id:06d}"

    ifsc_code = "SECB0000001"

    return render(
        request,
        'receipt.html',
        {
            'transaction': transaction_data,
            'user': user,
            'account_number': account_number,
            'ifsc_code': ifsc_code,
        }
    )