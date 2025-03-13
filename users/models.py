from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, AbstractBaseUser, PermissionsMixin

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
        ('MOBILIZATION', 'Mobilization')
    ]
    role = models.CharField(max_length=12, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)  # Optional email field
    is_approved = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    
    def generate_otp(self):
        # Generate a 6-digit OTP
        import random
        self.otp = str(random.randint(100000, 999999))
        self.otp_expiry = timezone.now() + timedelta(minutes=5)  # OTP expires in 5 minutes
        self.save()

    def is_otp_valid(self, otp):
        # Check if the OTP is valid and not expired
        return self.otp == otp and self.otp_expiry > timezone.now()
    
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
    customer_picture = models.ImageField(upload_to='customer_pic/', default='')
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

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
    
    
class OTP(models.Model):
    phone_number = models.CharField(max_length=10, unique=True)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    
    
    def is_valid(self):
        return (timezone.now() - self.created_at).seconds < 300 # Valid for 5 minutes
    