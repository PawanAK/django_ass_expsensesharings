from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class CustomUser(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex=r'^\d{10}$',
                                   message="Phone number must be exactly 10 digits without any symbols.")]
    )

    def __str__(self):
        return self.email


class Expense(models.Model):
    SPLIT_CHOICES = [
        ('EQUAL', 'Equal'),
        ('EXACT', 'Exact'),
        ('PERCENT', 'Percentage'),
    ]

    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    split_type = models.CharField(max_length=10, choices=SPLIT_CHOICES)
    paid_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='expenses_paid')

    def __str__(self):
        return f"{self.description} - {self.amount}"


class ExpenseSplit(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='splits')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.expense.description} - {self.user.username} - {self.amount}"