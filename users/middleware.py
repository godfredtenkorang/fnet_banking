from django.utils import timezone
from django.shortcuts import redirect
from django.urls import reverse

class OTPVerificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_otp_verified_today():
            # Redirect to OTP verification page if OTP is not verified within the last 24 hours
            return redirect(reverse('verify_otp'))
        return self.get_response(request)