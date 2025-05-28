from datetime import timedelta
from django.forms import ValidationError
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, AbstractBaseUser, PermissionsMixin

import random

from users.utils import convert_km_to_miles, convert_miles_to_km


BRANCHES = (
    ("DVLA", "DVLA"),
    ("HEAD OFFICE", "HEAD OFFICE"),
    ("KEJETIA", "KEJETIA"),
    ("MELCOM SANTASI", "MELCOM SANTASI"),
    ("MELCOM TANOSO", "MELCOM TANOSO"),
    ("MELCOM MANHYIA", "MELCOM MANHYIA"),
    ("MELCOM TAFO", "MELCOM TAFO"),
    ("AHODWO MELCOM", "AHODWO MELCOM"),
    ("ADUM MELCOM ANNEX", "ADUM MELCOM ANNEX"),
    ("ADUM MELCOM", "ADUM MELCOM"),
    ("MELCOM SUAME", "MELCOM SUAME"),
    ("KUMASI MALL MELCOM", "KUMASI MALL MELCOM"),
    ("MOBILIZATION TEAM", "MOBILIZATION TEAM"),
)

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('OWNER', 'Owner'),
        ('BRANCH', 'Branch'),
        ('CUSTOMER', 'Customer'),
        ('MOBILIZATION', 'Mobilization'),
        ('DRIVER', 'Driver'),
        ('ACCOUNTANT', 'Accountant'),
    ]
    role = models.CharField(max_length=12, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=15, unique=True)
    # first_name = models.CharField(max_length=100, null=True, blank=True)
    # last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)  # Optional email field
    is_approved = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    otp_verified_at = models.DateTimeField(blank=True, null=True)  # Timestamp of OTP verification
    
    def generate_otp(self):
        # Generate a 6-digit OTP
        import random
        self.otp = str(random.randint(100000, 999999))
        self.otp_expiry = timezone.now() + timedelta(minutes=5)  # OTP expires in 5 minutes
        self.save()

    def is_otp_valid(self, otp):
        # Check if the OTP is valid and not expired
        return self.otp == otp and self.otp_expiry > timezone.now()
    
    def is_otp_verified_today(self):
        # Check if the OTP was verified within the last 24 hours
        if self.otp_verified_at:
            return timezone.now() - self.otp_verified_at < timedelta(days=1)
        return False
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    def __str__(self):
        return self.phone_number

class Branch(models.Model):
    name = models.CharField(max_length=100, choices=BRANCHES)
    location = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
class Owner(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='owner')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    company_number = models.CharField(max_length=10, null=True, blank=True)
    digital_address = models.CharField(max_length=50, null=True, blank=True)
    agent_code = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.owner.phone_number

class Agent(models.Model):
    agent = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent')
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    company_number = models.CharField(max_length=10, null=True, blank=True)
    digital_address = models.CharField(max_length=50, null=True, blank=True)
    agent_code = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.agent.phone_number
    
class Mobilization(models.Model):
    mobilization = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mobilization')
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    company_number = models.CharField(max_length=10, null=True, blank=True)
    digital_address = models.CharField(max_length=50, null=True, blank=True)
    mobilization_code = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.full_name
    
class Driver(models.Model):
    driver = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver')
    email = models.EmailField(null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    company_number = models.CharField(max_length=10, null=True, blank=True)
    digital_address = models.CharField(max_length=50, null=True, blank=True)
    driver_code = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.driver.phone_number
    
class Accountant(models.Model):
    accountant = models.OneToOneField(User, on_delete=models.CASCADE, related_name='accountant')
    email = models.EmailField(null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    company_number = models.CharField(max_length=10, null=True, blank=True)
    digital_address = models.CharField(max_length=50, null=True, blank=True)
    accountant_code = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.accountant.phone_number

class Customer(models.Model):
    customer = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=True, blank=True)
    mobilization = models.ForeignKey(Mobilization, on_delete=models.CASCADE, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    customer_location = models.CharField(max_length=100, null=True, blank=True)
    digital_address = models.CharField(max_length=100, null=True, blank=True)
    id_type = models.CharField(max_length=20, null=True, blank=True)
    id_number = models.CharField(max_length=100, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    customer_picture = models.ImageField(upload_to='customer_pic/', default='', null=True, blank=True)
    customer_image = models.ImageField(upload_to='customer_image/', default='', null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    @classmethod
    def upcoming_birthdays(cls, days=5):
        """Get customers with birthdays in the next X days"""
        today = timezone.now().date()
        target_date = today + timedelta(days=days)
        
        # Handle year wrap-around (for December/January birthdays)
        if today.month == target_date.month:
            return cls.objects.filter(
                date_of_birth__month=today.month,
                date_of_birth__day__range=(today.day, target_date.day),
                phone_number__isnull=False
            ).exclude(phone_number='')
        else:
            return cls.objects.filter(
                models.Q(
                    date_of_birth__month=today.month,
                    date_of_birth__day__gte=today.day
                ) | models.Q(
                    date_of_birth__month=target_date.month,
                    date_of_birth__day__lte=target_date.day
                ),
                phone_number__isnull=False
            ).exclude(phone_number='')
    
    @property
    def days_until_birthday(self):
        """Calculate days until next birthday"""
        if not self.date_of_birth:
            return None
            
        today = timezone.now().date()
        next_birthday = self.date_of_birth.replace(year=today.year)
        
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
            
        return (next_birthday - today).days

    def __str__(self):
        return self.customer.phone_number
    

    
class MobilizationCustomer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mobilizationcustomer')
    mobilization = models.ForeignKey(Mobilization, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    customer_location = models.CharField(max_length=100, null=True, blank=True)
    digital_address = models.CharField(max_length=100, null=True, blank=True)
    id_type = models.CharField(max_length=20, null=True, blank=True)
    id_number = models.CharField(max_length=100, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    customer_picture = models.ImageField(upload_to='customer_pic/', default='')
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.full_name
    
class Vehicle(models.Model):
    UNIT_CHOICES = [
        ('km', 'Kilometers'),
        ('mi', 'Miles'),
    ]
    registration_number = models.CharField(max_length=20, unique=True)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    distance_unit = models.CharField(
        max_length=2,
        choices=UNIT_CHOICES,
        default='km',
        help_text="Unit of measurement for this vehicle's odometer"
    )
    # owner = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'OWNER'}, null=True, blank=True)
    oil_change_default = models.PositiveBigIntegerField(default=5000, help_text="Default mileage between oil changes (km)")
    last_oil_change_mileage = models.PositiveBigIntegerField(default=0, help_text="Mileage at last oil change (km)")
    last_oil_change_date = models.DateField(null=True, blank=True)
    
    
    
    @property
    def display_unit(self):
        return "km" if self.distance_unit == 'km' else "miles"
    
    @property
    def oil_change_default_display(self):
        return f"{self.oil_change_default} {self.display_unit}"
    
    def convert_to_display_unit(self, value):
        """Convert a value in km to the vehicle's display unit"""
        if self.distance_unit == 'mi':
            return convert_km_to_miles(value)
        return value
    
    def convert_from_display_unit(self, value):
        """Convert a value in the vehicle's display unit to km"""
        if self.distance_unit == 'mi':
            return convert_miles_to_km(value)
        return value
    
    
    def clean(self):
        if self.last_oil_change_mileage is not None and self.current_mileage is not None:
            if self.last_oil_change_mileage > self.current_mileage:
                raise ValidationError("Last oil change mileage cannot be greater than current mileage")
            
    def reset_oil_change_tracking(self, current_tracking):
        self.last_oil_change_mileage = current_tracking
        self.last_oil_change_date = timezone.now().date()
        self.save()
        
        
    
    @property
    def mileage_until_oil_change(self):
        # Ensure we have valid values for calculation
        if self.last_oil_change_mileage is None:
            return self.oil_change_default  # If never changed, use full interval
            
        current_mileage = self.current_mileage
        if current_mileage is None:
            return 0  # Can't calculate without current mileage
            
        miles_since_change = current_mileage - self.last_oil_change_mileage
        remaining = self.oil_change_default - miles_since_change
        return max(remaining, 0)  # Don't return negative numbers
    
    @property
    def current_mileage(self):
        if not self.pk:
            return None
        """Get the current mileage from the latest record"""
        latest_record = self.mileagerecord_set.order_by('-date').first()
        return latest_record.end_mileage if latest_record else None
    
    @property
    def miles_since_last_oil_change(self):
        """How many miles driven since last oil change"""
        if self.last_oil_change_mileage is None or self.current_mileage is None:
            return 0
        return self.current_mileage - self.last_oil_change_mileage
    
    @property
    def needs_oil_change(self):
        if self.mileage_until_oil_change == 0:
            return True
        return False
    
    
    def __str__(self):
        return f"{self.model} ({self.registration_number}) - {self.year}"
    
    
class OTP(models.Model):
    phone_number = models.CharField(max_length=10, unique=True)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    
    
    def is_valid(self):
        return (timezone.now() - self.created_at).seconds < 300 # Valid for 5 minutes
    
class OTPToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.otp = str(random.randint(100000, 999999))
            self.expires_at = timezone.now() + timedelta(minutes=5)
        super().save(*args, **kwargs)
        
    def is_valid(self):
        return not self.is_verified and timezone.now() < self.expires_at
    
    def __str__(self):
        return f"{self.user} - {self.otp}"