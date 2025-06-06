import requests
from django.conf import settings

def send_mobilization_bank_deposit_sms(mobilization, phone_number):
    endpoint = "https://api.mnotify.com/api/sms/quick"
    apiKey = settings.MNOTIFY_API_KEY
    payload = {
        "key": apiKey,
        "sender": 'Fnet',
        "recipient[]": '0549429685',
        "message": f"New Bank Deposit Request from {mobilization} - {phone_number}! \n\n" "Review Now.",
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
