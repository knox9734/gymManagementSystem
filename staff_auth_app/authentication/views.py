from authentication.models import CustomUser,Payment
from django.shortcuts import render, redirect
from datetime import date,timedelta,datetime
from django.contrib import messages
import random
from django.db.models import Sum
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse

def register_user(request):
    if request.method == 'POST':
        name = request.POST['name']
        birthday = parse(request.POST['birthday']).date()

        # Create a new CustomUser object with the provided data
        user = CustomUser(name=name, birthday=birthday)
        user.save()

        # Retrieve the user object using the username
        user = CustomUser.objects.get(username=user.username)
        random_offset = random.randint(91, 122)
        current_date = datetime.now().date()
        random_date = current_date - timedelta(days=random_offset)
        # Create a payment record for the new user with an initial amount of 0
        payment = Payment(user=user, payment_date=random_date, amount=2500)
        payment.save()

        # Add a success message
        messages.success(request, 'User registered successfully!')

    return render(request, 'registration.html')

def users(request):
    users = CustomUser.objects.all()
    payments = Payment.objects.all()
    return render(request, 'user.html', {'users': users, 'payments': payments})

def home(request):
    return render(request, 'home.html')

def add_payment(request, username):
    if request.method == 'POST':
        # Get the user based on the username
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            messages.error(request, 'User does not exist.')
            return redirect('user_list')

        # Get the payment data from the form
        amount = 2500

        # Check if the user already has a payment record
        try:
            payment = Payment.objects.get(user=user)
            payment.amount = amount
            payment.payment_date = date.today()
            payment.save()
        except Payment.DoesNotExist:
            # Create a new payment instance
            payment = Payment(user=user, payment_date=date.today(), amount=amount)
            payment.save()

        # Optionally, you can add a success message
        messages.success(request, 'Payment added successfully.')

        return redirect('users')
    else:
        # Handle GET request for the form display
        return render(request, 'add_payment.html')


# def payment_table(request):
#     payments = Payment.objects.select_related('user')
#     return render(request, 'payment_table.html', {'payments': payments})

def payment_table(request):
    payments = Payment.objects.select_related('user')
    current_date = date.today()
    start_date = current_date.replace(day=1)
    monthly_paid_amounts = []
    notPaid =0
    paid =0
    for payment in payments:
        if payment.payment_date < current_date - timedelta(days=30):
            payment.status = 'Not Paid'
            notPaid += 1
        else:
            payment.status = 'Paid'
            paid += 1
        # Calculate monthly paid amounts
    # Calculate monthly paid amounts
    monthly_paid_amounts = (
        Payment.objects
        .filter(payment_date__lte=current_date)  # Filter payments on or before current date
        .annotate(month=TruncMonth('payment_date'))  # Extract month from payment date
        .values('month')
        .annotate(total_amount=Sum('amount'))  # Calculate total amount for each month
        .order_by('month')
    )

    return render(request, 'payment_table.html', {'payments': payments,'notPaid':notPaid,'paid':paid,'monthly_paid_amounts': monthly_paid_amounts})

def delete_user(request, username):
    if request.method == 'POST':
        try:
            user = CustomUser.objects.get(username=username)
            payments = Payment.objects.filter(user=user)
            payments.delete()  # Delete all payments associated with the user
            user.delete()  # Delete the user
            # Optionally, you can add a success message
            messages.success(request, 'User and associated payments deleted successfully.')
        except CustomUser.DoesNotExist:
            messages.error(request, 'User does not exist.')
        return redirect('users')
    else:
        return render(request, 'user_list.html')