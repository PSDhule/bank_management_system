from django.db import models


# USER MODEL
class User(models.Model):

    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    )

    name = models.CharField(max_length=100)

    email = models.EmailField(unique=True)

    password = models.CharField(max_length=100)

    balance = models.IntegerField(default=0)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='customer'
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    account_status = models.CharField(
        max_length=20,
        default='Active'
    )

    account_created = models.BooleanField(
    default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


# TRANSACTION MODEL
class Transaction(models.Model):

    TRANSACTION_TYPES = (
        ('Deposit', 'Deposit'),
        ('Withdraw', 'Withdraw'),
        ('Transfer', 'Transfer'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    type = models.CharField(
        max_length=30,
        choices=TRANSACTION_TYPES
    )

    amount = models.IntegerField()

    recipient = models.CharField(
        max_length=100,
        blank=True
    )

    reference = models.CharField(
        max_length=100,
        blank=True
    )

    date = models.DateTimeField(
        auto_now_add=True
    )


# TRANSFER MODEL
class Transfer(models.Model):

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_transfers'
    )

    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_transfers'
    )

    amount = models.IntegerField()

    reference = models.CharField(
        max_length=100, default=''
    )

    status = models.CharField(
        max_length=20,
        default='Completed'
    )

    date = models.DateTimeField(
        auto_now_add=True
    )

