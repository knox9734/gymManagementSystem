from authentication.models import CustomUser,Payment
from django.shortcuts import render, redirect,HttpResponse
from datetime import date,timedelta,datetime
from django.contrib import messages
import random
from django.db.models import Sum
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from dateutil.parser import parse
import os
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
import requests
from pyzbar.pyzbar import decode
import cv2
from django.utils import timezone
import pywhatkit as pwk
import paho.mqtt.client as mqtt
import time
import serial
arduino = serial.Serial(port='COM9', baudrate=9600, timeout=.1)
def register_user(request):
    if request.method == 'POST':
        name = request.POST['name']
        birthday = parse(request.POST['birthday']).date()
        phone_number = request.POST['phone_number']
        # Create a new CustomUser object with the provided data
        user = CustomUser(name=name, birthday=birthday,phone_number=phone_number )
        user.save()

        # Retrieve the user object using the username
        user = CustomUser.objects.get(username=user.username)
        random_offset = random.randint(91, 122)
        current_date = datetime.now().date()
        random_date = current_date - timedelta(days=random_offset)
        # Create a payment record for the new user with an initial amount of 0
        payment = Payment(user=user, payment_date=random_date, amount=2500)
        payment.save()

        # Generate bar code 
        barcode_class = barcode.get_barcode_class('code128')
        generated_barcode = barcode_class(user.username, writer=ImageWriter())

        # Save the barcode as a PNG file
        filename = user.name
        current_path = os.getcwd()
        filepath = os.path.join(current_path, 'media', filename)  # Constructing the path
        generated_barcode.save(filepath)

        # Assign the barcode and save the customer record
        user.barcode = filename
        barcode_image_url = '/media/' + filename + '.png'
        file_path = filepath + '.png'
        print(file_path)
        font_name='OpenSans_Condensed-Bold.ttf'
        font_path = os.path.join(current_path, 'static', font_name)
        print(font_path)
        # Append user's name to the barcode image
        barcode_image = Image.open(file_path)
        draw = ImageDraw.Draw(barcode_image)
        font_size = 32  # Increase the font size to 16
        font = ImageFont.truetype(font_path, size=font_size)
        text = user.name
        text_width, text_height = draw.textsize(text, font=font)
        text_position = (barcode_image.width - text_width, barcode_image.height - text_height)
        draw.text(text_position, text, font=font, fill=(0, 0, 0))

        # Save the modified barcode image
        barcode_image.save(file_path)
        
        # The path to the modified barcode image
        

        # Your ImgBB API key
        api_key = '7fe048ffe10aaf71d769bd62c54adb26'

        # The path to the modified barcode image
        image_path = file_path

        # Upload the image to ImgBB
        with open(image_path, 'rb') as file:
            response = requests.post(
                "https://api.imgbb.com/1/upload",
                params={"key": api_key},
                files={"image": file}
            )

        # Get the image URL from the response
        image_url = response.json()["data"]["url"]

        print(f"Image URL: {image_url}")
        # # Your Twilio account SID and auth token
        # account_sid = 'ACd5fd9bc77397dfb5e6c464251d87d358'
        # auth_token = '8da1176dac2f4cb208104c95ea4a089c'
        # client = Client(account_sid, auth_token)

        # message = client.messages.create(
        # from_='whatsapp:+14155238886',
        # body='Your Registered bar code for User Registration | Dolphin Fitness Gym',
        # # media_url=['https://images.unsplash.com/photo-1545093149-618ce3bcf49d?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=668&q=80'],
        # media_url=[image_url],
        # to='whatsapp:+94776070740'
        # )
        
        new_phone_number = "+94" + phone_number[1:]
        whtspp_msg = "Here is your registered bar code for User Registration | Dolphin Fitness Gym : "+image_url + " And Your Registration number is : "+user.username
        # print(message.sid)
        send_whatsapp_message(new_phone_number, whtspp_msg)
        # pywhatkit.sendwhatmsg_instantly("+94776070740", "Hello, this is a test message")
        
        # Add a success message
        messages.success(request, 'User registered successfully!')

    return render(request, 'registration.html')

def send_whatsapp_message(number, message):
    pwk.sendwhatmsg_instantly(f"+{number}", message)

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

        return redirect('payment_list')
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
    
def upload_image(request):
    if request.method == 'POST' and 'image' in request.FILES:
        image = request.FILES['image']

        # Save the uploaded image to a temporary location
        filename = 'temp.jpg'
        current_path = os.getcwd()
        image_path = os.path.join(current_path, 'media', filename)

        # image_path = os.path.join(settings.MEDIA_ROOT, 'uploaded_image.jpg')
        with open(image_path, 'wb') as file:
            for chunk in image.chunks():
                file.write(chunk)

        # Call the BarcodeReader function with the image
        img = cv2.imread(image_path)
        detected_barcodes = decode(img)

        if not detected_barcodes:
            barcode_data = '0'
            return no_data(request)
            # os.remove(image_path)
        else:
            # os.remove(image_path)
            barcode_data = []
            for barcode in detected_barcodes:
                barcode_data.append(barcode.data)
        print('data in barcode : '+str(barcode_data))
        customer_details = find_customer_by_barcode(barcode_data)
        print(type(customer_details))
        

        if customer_details is not None:
            if customer_details:
                print("customer found:", customer_details.name)
                payment_status = get_payment_data(customer_details.username)
                print(payment_status)
                # door_open = payment_status.paid
                value = '1'
                if not payment_status['paid']:
                    value = '0'
                door_open(value)
                return render(request, 'upload_success.html', {'payment_status': payment_status})
            else:
                print("customer not found")
                return render(request, 'upload_image.html')
        else:
            return render(request, 'upload_image.html')

    return render(request, 'upload_image.html')
    
def find_customer_by_barcode(barcode_data):
    cleaned_data = str(barcode_data[0]).replace("b", "").replace("'", "")
    try:
        customer = CustomUser.objects.get(username=cleaned_data)
        
        return customer
    except CustomUser.DoesNotExist:
        return None
    
def payment_list(request):
    current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_month_end = (current_month_start + timezone.timedelta(days=32)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    users = CustomUser.objects.all()  # Replace `CustomUser` with your actual user model

    payment_status = []
    for user in users:
        payment = Payment.objects.filter(user=user, payment_date__gte=current_month_start, payment_date__lt=current_month_end).first()
        user_status = {
            'user': user,
            'paid': payment is not None,
        }
        payment_status.append(user_status)

    context = {
        'payment_status': payment_status,
    }

    return render(request, 'payment_list.html', context)

def get_payment_data(username):
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_month_end = (current_month_start + timedelta(days=32)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    user = CustomUser.objects.get(username=username)  # Replace `CustomUser` with your actual user model

    payment_status = []
    
    payment = Payment.objects.filter(user=user, payment_date__gte=current_month_start, payment_date__lt=current_month_end).first()
    
    if payment and payment.payment_date.month == current_month_start.month:
        payment_status = {
            'user': user.name,
            'paid': True,
        }
    else:
        payment_status = {
            'user': user.name,
            'paid': False,
        }

    return payment_status



def write_read(x):
    
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
    data = arduino.readline()
    return data

def blink_led():
    arduino.write(b'1')  # Sending '1' to the Arduino to trigger the LED blink
    time.sleep(0.05)
    data = arduino.readline()
    return data

def door_open(value):
    blinking_done = False

    while not blinking_done:
        random_value = '2'  # Change this to any random value other than '1'
        response = write_read(random_value)
        time.sleep(1)
        random_value = '2'  # Change this to any random value other than '1'
        response = write_read(random_value)
        time.sleep(1)
        print("Sent random value:", random_value)

        num = value
        time.sleep(1)
        if num == '1':
            response = blink_led()
            print("door opening:", response)
            blinking_done = True
        elif num == '0':
            response = write_read('0')
            print("not paid alarm:", response)
            blinking_done = True
        else:
            print("Invalid input. Only '1' or '0' triggers the LED action.")

def no_data(request):
    # Clear the cache headers to prevent caching
    response = HttpResponse(render(request, 'no_data.html'))
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response