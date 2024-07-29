from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import CustomUser, Expense, ExpenseSplit
import json
import csv
from decimal import Decimal, InvalidOperation
import re


@csrf_exempt
@require_http_methods(["POST"])
def create_user(request):
    data = json.loads(request.body)
    try:
        validate_email(data['email'])
        if CustomUser.objects.filter(email=data['email']).exists():
            return JsonResponse({'error': 'Email already exists'}, status=400)
        if not data['name'] or len(data['name']) > 255:
            return JsonResponse({'error': 'Invalid name'}, status=400)
        if not data['mobile_number'] or not re.match(r'^\+?1?\d{9,15}$', data['mobile_number']):
            return JsonResponse({'error': 'Invalid mobile number'}, status=400)

        user = CustomUser.objects.create_user(
            username=data['email'],
            email=data['email'],
            password=data['password'],
            name=data['name'],
            mobile_number=data['mobile_number']
        )
        return JsonResponse({'id': user.id, 'message': 'User created successfully'}, status=201)
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["GET"])
def get_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    return JsonResponse({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'mobile_number': user.mobile_number
    })


@csrf_exempt
@require_http_methods(["POST"])
def create_expense(request):
    data = json.loads(request.body)

    # Validate input
    required_fields = ['description', 'amount', 'split_type', 'paid_by', 'participants']
    if not all(field in data for field in required_fields):
        return JsonResponse({'error': 'Missing required fields'}, status=400)

    try:
        total_amount = Decimal(data['amount'])
        if total_amount <= 0:
            return JsonResponse({'error': 'Amount must be positive'}, status=400)
    except InvalidOperation:
        return JsonResponse({'error': 'Invalid amount'}, status=400)

    split_type = data['split_type']
    participants = data['participants']

    if not CustomUser.objects.filter(id=data['paid_by']).exists():
        return JsonResponse({'error': 'Invalid user paying for the expense'}, status=400)

    if not all(CustomUser.objects.filter(id=user_id).exists() for user_id in participants):
        return JsonResponse({'error': 'Invalid participants'}, status=400)

    # Calculate splits based on split type
    if split_type == 'EQUAL':
        num_participants = len(participants)
        amount_per_person = total_amount / num_participants
        splits = [{'user': user_id, 'amount': amount_per_person} for user_id in participants]

    elif split_type == 'EXACT':
        if 'splits' not in data:
            return JsonResponse({'error': 'Splits must be provided for EXACT split type'}, status=400)
        splits = data['splits']
        if sum(Decimal(split['amount']) for split in splits) != total_amount:
            return JsonResponse({'error': 'Sum of splits must equal total amount'}, status=400)

    elif split_type == 'PERCENT':
        if 'splits' not in data:
            return JsonResponse({'error': 'Splits must be provided for PERCENT split type'}, status=400)
        splits = data['splits']
        if sum(Decimal(split['percent']) for split in splits) != 100:
            return JsonResponse({'error': 'Percentages must sum to 100'}, status=400)
        splits = [{'user': split['user'], 'amount': (Decimal(split['percent']) / 100) * total_amount} for split in
                  splits]

    else:
        return JsonResponse({'error': 'Invalid split type'}, status=400)

    # Create expense and splits
    try:
        expense = Expense.objects.create(
            description=data['description'],
            amount=total_amount,
            split_type=split_type,
            paid_by_id=data['paid_by']
        )

        for split in splits:
            ExpenseSplit.objects.create(
                expense=expense,
                user_id=split['user'],
                amount=split['amount']
            )
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'id': expense.id, 'message': 'Expense created successfully'}, status=201)


@require_http_methods(["GET"])
def get_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    splits = expense.splits.all()

    response_data = {
        'id': expense.id,
        'description': expense.description,
        'amount': str(expense.amount),
        'split_type': expense.split_type,
        'paid_by': expense.paid_by.name,
        'splits': [
            {
                'user': split.user.name,
                'amount': str(split.amount)
            } for split in splits
        ]
    }

    return JsonResponse(response_data)


@require_http_methods(["GET"])
def get_user_expenses(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    expenses_paid = Expense.objects.filter(paid_by=user)
    expenses_involved = Expense.objects.filter(splits__user=user)

    return JsonResponse({
        'expenses_paid': [
            {
                'id': expense.id,
                'description': expense.description,
                'amount': str(expense.amount),
                'date': expense.date
            } for expense in expenses_paid
        ],
        'expenses_involved': [
            {
                'id': expense.id,
                'description': expense.description,
                'amount': str(expense.amount),
                'date': expense.date,
                'owed_amount': str(expense.splits.get(user=user).amount)
            } for expense in expenses_involved
        ]
    })


@require_http_methods(["GET"])
def get_overall_expenses(request):
    expenses = Expense.objects.all()
    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    return JsonResponse({
        'total': str(total),
        'expenses': [
            {
                'id': expense.id,
                'description': expense.description,
                'amount': str(expense.amount),
                'date': expense.date.strftime('%Y-%m-%d'),
                'paid_by': expense.paid_by.name
            } for expense in expenses
        ]
    })


@require_http_methods(["GET"])
def download_balance_sheet(request):
    users = CustomUser.objects.all()
    expenses = Expense.objects.all().prefetch_related('splits')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="balance_sheet.csv"'

    writer = csv.writer(response)
    writer.writerow(['User', 'Total Paid', 'Total Owed', 'Balance', 'Individual Expenses'])

    for user in users:
        total_paid = Expense.objects.filter(paid_by=user).aggregate(Sum('amount'))['amount__sum'] or 0
        total_owed = ExpenseSplit.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
        balance = total_paid - total_owed

        individual_expenses = []
        for expense in expenses:
            split = expense.splits.filter(user=user).first()
            if split:
                individual_expenses.append(f"{expense.description}: {split.amount}")

        writer.writerow([
            user.name,
            total_paid,
            total_owed,
            balance,
            '; '.join(individual_expenses)
        ])

    # Add overall expenses
    total_expenses = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    writer.writerow([])
    writer.writerow(['Overall Expenses', total_expenses])

    return response


@require_http_methods(["GET"])
def get_balance_details(request):
    users = CustomUser.objects.all()
    expenses = Expense.objects.all().prefetch_related('splits')

    balance_details = []
    overall_total = 0

    for user in users:

        total_paid = Expense.objects.filter(paid_by=user).aggregate(Sum('amount'))['amount__sum'] or 0
        total_owed = ExpenseSplit.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
        balance = total_paid - total_owed

        individual_expenses = []
        for expense in expenses:
            split = expense.splits.filter(user=user).first()
            if split:
                individual_expenses.append({
                    'description': expense.description,
                    'amount': str(split.amount),
                    'date': expense.date.strftime('%Y-%m-%d')
                })

        balance_details.append({
            'user': user.name,
            'email': user.email,
            'total_paid': str(total_paid),
            'total_owed': str(total_owed),
            'balance': str(balance),
            'individual_expenses': individual_expenses
        })

        overall_total += total_paid

    return JsonResponse({
        'balance_details': balance_details,
        'overall_total': str(overall_total)
    })