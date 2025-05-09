import requests
from django.conf import settings
from django.core.mail import send_mail
from django.conf import settings
import random



def send_otp(phone_number, otp):
    endpoint = "https://api.mnotify.com/api/sms/quick"
    apiKey = settings.MNOTIFY_API_KEY
    payload = {
        "key": apiKey,
        "sender": 'Fnet',
        "recipient[]": phone_number,
        "message": f"Your OTP is: {otp}",
        "is_schedule": False,
        "schedule_date": ''
    }
    

    url = endpoint + '?key=' + apiKey
    
   
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Error sending SMS: {e}")
        return None
    
def send_otp_via_email(email, otp):
    subject = 'Your OTP for Login'
    message = f"Your OTP code is: {otp}. Please use it to log in."
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    
    send_mail(subject, message, from_email, recipient_list)
    


def generate_otp(length=6):
    """Generate a random numeric OTP of given length."""
    return ''.join(str(random.randint(0, 9)) for _ in range(length))


def send_otp_sms(phone_number, otp):
    """
    Send OTP to the given phone number.
    Replace the below code with your SMS provider's API integration.
    """
    endpoint = "https://api.mnotify.com/api/sms/quick"
    apiKey = settings.MNOTIFY_API_KEY
    payload = {
        "key": apiKey,
        "sender": 'Fnet',
        "recipient[]": phone_number,
        "message": f"Your OTP is: {otp} \n",
        "is_schedule": False,
        "schedule_date": ''
    }
    

    url = endpoint + '?key=' + apiKey
    
   
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Error sending SMS: {e}")
        return None
    
    
# def send_otp(phone_number):
#     otp = random.randint(100000, 999999)
#     OTP.objects.update_or_create(phone=phone_number, defaults={"otp_code": otp})
#     """
#     Send OTP to the given phone number.
#     Replace the below code with your SMS provider's API integration.
#     """
#     endpoint = "https://api.mnotify.com/api/sms/quick"
#     apiKey = settings.MNOTIFY_API_KEY
#     payload = {
#         "key": apiKey,
#         "sender": 'Fnet',
#         "recipient[]": phone_number,
#         "message": f"Your OTP code is {otp}. Valid for 5 minutes.",
#         "is_schedule": False,
#         "schedule_date": ''
#     }
    

#     url = endpoint + '?key=' + apiKey
    
   
#     try:
#         response = requests.post(url, data=payload)
#         response.raise_for_status()
        
#         return response.json()
    
#     except requests.exceptions.RequestException as e:
#         print(f"Error sending SMS: {e}")
#         return None


def send_reset_password_otp_sms(phone_number, otp):
    """
    Send OTP to the given phone number.
    Replace the below code with your SMS provider's API integration.
    """
    endpoint = "https://api.mnotify.com/api/sms/quick"
    apiKey = settings.MNOTIFY_API_KEY
    payload = {
        "key": apiKey,
        "sender": 'Fnet',
        "recipient[]": phone_number,
        "message": f"Your OTP for password change is: {otp} \n",
        "is_schedule": False,
        "schedule_date": ''
    }
    

    url = endpoint + '?key=' + apiKey
    
   
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Error sending SMS: {e}")
        return None
    

def convert_km_to_miles(km):
    return km * 0.621371

def convert_miles_to_km(miles):
    return miles * 1.60934

def convert_to_common_unit(value, from_unit, to_unit='km'):
    if from_unit == to_unit:
        return value
    if from_unit == 'km' and to_unit == 'mi':
        return convert_km_to_miles(value)
    if from_unit == 'mi' and to_unit == 'km':
        return convert_miles_to_km(value)
    return value