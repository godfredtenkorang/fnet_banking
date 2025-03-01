from django.db import models
from django.contrib.auth.models import AbstractUser

BRANCHES = (
    ("Please select cash at location", "Please select cash at location"),
    ("DVLA", "DVLA"),
    ("HEAD OFFICE", "HEAD OFFICE"),
    ("KEJETIA", "KEJETIA"),
    ("MELCOM SANTASI", "MELCOM SANTASI"),
    ("MELCOM TANOSO", "MELCOM TANOSO"),
    ("MELCOM MANHYIA", "MELCOM MANHYIA"),
    ("MELCOM TAFO", "MELCOM TAFO"),
    ("AHODWO MELCOM", "AHODWO MELCOM"),
    ("ADUM MELCOM ANNEX", "ADUM MELCOM ANNEX"),
    ("MELCOM SUAME", "MELCOM SUAME"),
    ("KUMASI MALL MELCOM", "KUMASI MALL MELCOM"),
    ("MOBILIZATION", "MOBILIZATION"),
)

class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('OWNER', 'Owner'),
        ('AGENT', 'Agent'),
        ('CUSTOMER', 'Customer'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_approved = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, unique=True)
    
    REQUIRED_FIELDS = ['phone_number']
    USERNAME_FIELD = 'username'
    
    
    def __str__(self):
        return self.username

class Branch(models.Model):
    name = models.CharField(max_length=100, choices=BRANCHES)
    location = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
class Owner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='owner')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    company_number = models.CharField(max_length=10, null=True, blank=True)
    digital_address = models.CharField(max_length=50, null=True, blank=True)
    agent_code = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.user.username

class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent')
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
        return self.user.username

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
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