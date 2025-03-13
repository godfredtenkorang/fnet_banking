import requests
from django.conf import settings
from django.core.mail import send_mail
from django.conf import settings


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
    