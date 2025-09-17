from datetime import timedelta
from django.forms import ValidationError
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, AbstractBaseUser, PermissionsMixin

import random

from users.utils import convert_km_to_miles, convert_miles_to_km

import os
import json
from django.conf import settings
from django.db import transaction
from django.core.serializers import serialize, deserialize
import base64


BRANCHES = (
    ("DVLA", "DVLA"),
    ("HEAD OFFICE", "HEAD OFFICE"),
    ("KEJETIA", "KEJETIA"),
    ("MELCOM SANTASI", "MELCOM SANTASI"),
    ("MELCOM TANOSO", "MELCOM TANOSO"),
    ("MELCOM MANHYIA", "MELCOM MANHYIA"),
    ("MELCOM TAFO", "MELCOM TAFO"),
    ("AHODWO MELCOM", "AHODWO MELCOM"),
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
    
    @classmethod
    def export_to_json(cls, filename=None, include_sensitive=False):
        """Export all users to JSON file"""
        if not filename:
            filename = f'users_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        users = cls.objects.all()
        
        if include_sensitive:
            data = serialize('json', users)
        else:
            # Create safe export
            safe_data = []
            for user in users:
                safe_user = {
                    'model': 'auth.user',
                    'pk': user.pk,
                    'fields': {
                        'role': user.role,
                        'phone_number': user.phone_number,
                        'email': user.email,
                        'is_approved': user.is_approved,
                        'is_blocked': user.is_blocked,
                        'is_staff': user.is_staff,
                        'is_active': user.is_active,
                        'last_login': user.last_login.isoformat() if user.last_login else None,
                        'date_joined': user.date_joined.isoformat() if user.date_joined else None,
                    }
                }
                safe_data.append(safe_user)
            data = json.dumps(safe_data)
        
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        filepath = os.path.join(backup_dir, filename)
        with open(filepath, 'w') as f:
            f.write(data)
        
        return filepath
    
    @classmethod
    def import_from_json(cls, filename, clear_existing=False, skip_duplicates=False):
        """Import users from JSON file"""
        filepath = os.path.join(settings.BASE_DIR, 'backups', filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Backup file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            data = f.read()
        
        if clear_existing:
            cls.objects.all().delete()
        
        count = 0
        skipped = 0
        with transaction.atomic():
            for obj in deserialize('json', data):
                user_data = obj.object
                
                if skip_duplicates and cls.objects.filter(phone_number=user_data.phone_number).exists():
                    skipped += 1
                    continue
                
                # Set default password if not properly hashed
                if not user_data.password.startswith(('pbkdf2_', 'bcrypt$', 'argon2$')):
                    user_data.set_password('default_password')
                
                obj.save()
                count += 1
        
        return count, skipped
    
    def __str__(self):
        return self.phone_number

class Branch(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
    @classmethod
    def export_to_json(cls, filename=None):
        """Export all branches to JSON file"""
        if not filename:
            filename = f'branches_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        branches = cls.objects.all()
        data = serialize('json', branches)
        
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        filepath = os.path.join(backup_dir, filename)
        with open(filepath, 'w') as f:
            f.write(data)
        
        return filepath
    
    @classmethod
    def import_from_json(cls, filename, clear_existing=False, skip_duplicates=False, update_existing=False):
        """Import branches from JSON file"""
        filepath = os.path.join(settings.BASE_DIR, 'backups', filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Backup file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            data = f.read()
        
        if clear_existing:
            cls.objects.all().delete()
        
        count = 0
        updated = 0
        skipped = 0
        with transaction.atomic():
            for obj in deserialize('json', data):
                branch_data = obj.object
                
                # Check for existing branch by name
                existing_branch = None
                if branch_data.name:
                    existing_branch = cls.objects.filter(name=branch_data.name).first()
                
                if existing_branch:
                    if skip_duplicates:
                        skipped += 1
                        continue
                    elif update_existing:
                        # Update existing branch
                        existing_branch.location = branch_data.location
                        existing_branch.save()
                        updated += 1
                        continue
                
                obj.save()
                count += 1
        
        return count, updated, skipped
    
    @classmethod
    def create_default_branches(cls):
        """Create default branches from BRANCHES tuple"""
        created_count = 0
        for branch_name, _ in BRANCHES:
            branch, created = cls.objects.get_or_create(
                name=branch_name,
                defaults={'location': branch_name}  # Using name as location for defaults
            )
            if created:
                created_count += 1
        
        return created_count
    
class Owner(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='owner')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    company_number = models.CharField(max_length=10, null=True, blank=True)
    digital_address = models.CharField(max_length=50, null=True, blank=True)
    agent_code = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.owner.phone_number
    
    @classmethod
    def export_to_json(cls, filename=None, include_related=False):
        """Export all owners to JSON file"""
        if not filename:
            filename = f'owners_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        owners = cls.objects.all().select_related('owner', 'branch')
        
        if include_related:
            data = serialize('json', owners, use_natural_foreign_keys=True)
        else:
            custom_data = []
            for owner in owners:
                owner_data = {
                    'model': 'your_app.owner',
                    'pk': owner.pk,
                    'fields': {
                        'owner': owner.owner_id,
                        'branch': owner.branch_id if owner.branch else None,
                        'email': owner.email,
                        'full_name': owner.full_name,
                        'phone_number': owner.phone_number,
                        'company_name': owner.company_name,
                        'company_number': owner.company_number,
                        'digital_address': owner.digital_address,
                        'agent_code': owner.agent_code,
                    }
                }
                custom_data.append(owner_data)
            data = json.dumps(custom_data)
        
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        filepath = os.path.join(backup_dir, filename)
        with open(filepath, 'w') as f:
            f.write(data)
        
        return filepath
    
    @classmethod
    def import_from_json(cls, filename, clear_existing=False, skip_duplicates=False, 
                        update_existing=False, skip_missing_users=False):
        """Import owners from JSON file"""
        filepath = os.path.join(settings.BASE_DIR, 'backups', filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Backup file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            data = f.read()
        
        if clear_existing:
            cls.objects.all().delete()
        
        count = 0
        updated = 0
        skipped = 0
        missing_users = 0
        with transaction.atomic():
            for obj in deserialize('json', data):
                owner_data = obj.object
                
                # Check if user exists
                try:
                    user = User.objects.get(pk=owner_data.owner_id)
                except User.DoesNotExist:
                    if skip_missing_users:
                        missing_users += 1
                        continue
                    else:
                        raise ValueError(f"User with ID {owner_data.owner_id} does not exist")
                
                # Check for existing owner by user
                existing_owner = cls.objects.filter(owner=user).first()
                
                if existing_owner:
                    if skip_duplicates:
                        skipped += 1
                        continue
                    elif update_existing:
                        # Update existing owner
                        existing_owner.branch = owner_data.branch
                        existing_owner.email = owner_data.email
                        existing_owner.full_name = owner_data.full_name
                        existing_owner.phone_number = owner_data.phone_number
                        existing_owner.company_name = owner_data.company_name
                        existing_owner.company_number = owner_data.company_number
                        existing_owner.digital_address = owner_data.digital_address
                        existing_owner.agent_code = owner_data.agent_code
                        existing_owner.save()
                        updated += 1
                        continue
                
                obj.save()
                count += 1
        
        return count, updated, skipped, missing_users

class Agent(models.Model):
    agent = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent')
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    company_number = models.CharField(max_length=10, null=True, blank=True)
    digital_address = models.CharField(max_length=50, null=True, blank=True)
    agent_code = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.agent.phone_number
    
    @classmethod
    def export_to_json(cls, filename=None, include_related=False):
        """Export all agents to JSON file"""
        if not filename:
            filename = f'agents_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        agents = cls.objects.all().select_related('agent', 'owner', 'branch')
        
        if include_related:
            data = serialize('json', agents, use_natural_foreign_keys=True)
        else:
            custom_data = []
            for agent in agents:
                agent_data = {
                    'model': 'your_app.agent',
                    'pk': agent.pk,
                    'fields': {
                        'agent': agent.agent_id,
                        'owner': agent.owner_id,
                        'branch': agent.branch_id if agent.branch else None,
                        'email': agent.email,
                        'full_name': agent.full_name,
                        'phone_number': agent.phone_number,
                        'company_name': agent.company_name,
                        'company_number': agent.company_number,
                        'digital_address': agent.digital_address,
                        'agent_code': agent.agent_code,
                    }
                }
                custom_data.append(agent_data)
            data = json.dumps(custom_data)
        
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        filepath = os.path.join(backup_dir, filename)
        with open(filepath, 'w') as f:
            f.write(data)
        
        return filepath
    
    @classmethod
    def import_from_json(cls, filename, clear_existing=False, skip_duplicates=False, 
                        update_existing=False, skip_missing_users=False, skip_missing_owners=False):
        """Import agents from JSON file"""
        filepath = os.path.join(settings.BASE_DIR, 'backups', filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Backup file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            data = f.read()
        
        if clear_existing:
            cls.objects.all().delete()
        
        count = 0
        updated = 0
        skipped = 0
        missing_users = 0
        missing_owners = 0
        with transaction.atomic():
            for obj in deserialize('json', data):
                agent_data = obj.object
                
                # Check if user exists
                try:
                    user = User.objects.get(pk=agent_data.agent_id)
                except User.DoesNotExist:
                    if skip_missing_users:
                        missing_users += 1
                        continue
                    else:
                        raise ValueError(f"User with ID {agent_data.agent_id} does not exist")
                
                # Check if owner exists
                try:
                    owner = Owner.objects.get(pk=agent_data.owner_id)
                except Owner.DoesNotExist:
                    if skip_missing_owners:
                        missing_owners += 1
                        continue
                    else:
                        raise ValueError(f"Owner with ID {agent_data.owner_id} does not exist")
                
                # Check for existing agent by user
                existing_agent = cls.objects.filter(agent=user).first()
                
                if existing_agent:
                    if skip_duplicates:
                        skipped += 1
                        continue
                    elif update_existing:
                        # Update existing agent
                        existing_agent.owner = owner
                        existing_agent.branch = agent_data.branch
                        existing_agent.email = agent_data.email
                        existing_agent.full_name = agent_data.full_name
                        existing_agent.phone_number = agent_data.phone_number
                        existing_agent.company_name = agent_data.company_name
                        existing_agent.company_number = agent_data.company_number
                        existing_agent.digital_address = agent_data.digital_address
                        existing_agent.agent_code = agent_data.agent_code
                        existing_agent.save()
                        updated += 1
                        continue
                
                obj.save()
                count += 1
        
        return count, updated, skipped, missing_users, missing_owners
    
class Mobilization(models.Model):
    mobilization = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mobilization')
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    company_number = models.CharField(max_length=10, null=True, blank=True)
    digital_address = models.CharField(max_length=50, null=True, blank=True)
    mobilization_code = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.full_name
    
    @classmethod
    def export_to_json(cls, filename=None, include_related=False):
        """Export all mobilizations to JSON file"""
        if not filename:
            filename = f'mobilizations_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        mobilizations = cls.objects.all().select_related('mobilization', 'owner', 'branch')
        
        if include_related:
            data = serialize('json', mobilizations, use_natural_foreign_keys=True)
        else:
            custom_data = []
            for mob in mobilizations:
                mob_data = {
                    'model': 'your_app.mobilization',
                    'pk': mob.pk,
                    'fields': {
                        'mobilization': mob.mobilization_id,
                        'owner': mob.owner_id if mob.owner else None,
                        'branch': mob.branch_id if mob.branch else None,
                        'email': mob.email,
                        'full_name': mob.full_name,
                        'phone_number': mob.phone_number,
                        'company_name': mob.company_name,
                        'company_number': mob.company_number,
                        'digital_address': mob.digital_address,
                        'mobilization_code': mob.mobilization_code,
                    }
                }
                custom_data.append(mob_data)
            data = json.dumps(custom_data)
        
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        filepath = os.path.join(backup_dir, filename)
        with open(filepath, 'w') as f:
            f.write(data)
        
        return filepath
    
    @classmethod
    def import_from_json(cls, filename, clear_existing=False, skip_duplicates=False, 
                        update_existing=False, skip_missing_users=False, skip_missing_owners=False):
        """Import mobilizations from JSON file"""
        filepath = os.path.join(settings.BASE_DIR, 'backups', filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Backup file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            data = f.read()
        
        if clear_existing:
            cls.objects.all().delete()
        
        count = 0
        updated = 0
        skipped = 0
        missing_users = 0
        missing_owners = 0
        with transaction.atomic():
            for obj in deserialize('json', data):
                mob_data = obj.object
                
                # Check if user exists
                try:
                    user = User.objects.get(pk=mob_data.mobilization_id)
                except User.DoesNotExist:
                    if skip_missing_users:
                        missing_users += 1
                        continue
                    else:
                        raise ValueError(f"User with ID {mob_data.mobilization_id} does not exist")
                
                # Check if owner exists (if specified)
                owner = None
                if mob_data.owner_id:
                    try:
                        owner = Owner.objects.get(pk=mob_data.owner_id)
                    except Owner.DoesNotExist:
                        if skip_missing_owners:
                            missing_owners += 1
                            continue
                        else:
                            raise ValueError(f"Owner with ID {mob_data.owner_id} does not exist")
                
                # Check for existing mobilization by user
                existing_mob = cls.objects.filter(mobilization=user).first()
                
                if existing_mob:
                    if skip_duplicates:
                        skipped += 1
                        continue
                    elif update_existing:
                        # Update existing mobilization
                        existing_mob.owner = owner
                        existing_mob.branch = mob_data.branch
                        existing_mob.email = mob_data.email
                        existing_mob.full_name = mob_data.full_name
                        existing_mob.phone_number = mob_data.phone_number
                        existing_mob.company_name = mob_data.company_name
                        existing_mob.company_number = mob_data.company_number
                        existing_mob.digital_address = mob_data.digital_address
                        existing_mob.mobilization_code = mob_data.mobilization_code
                        existing_mob.save()
                        updated += 1
                        continue
                
                obj.save()
                count += 1
        
        return count, updated, skipped, missing_users, missing_owners
    
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
    
    @classmethod
    def export_to_json(cls, filename=None, include_related=False):
        """Export all drivers to JSON file"""
        if not filename:
            filename = f'drivers_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        drivers = cls.objects.all().select_related('driver')
        
        if include_related:
            data = serialize('json', drivers, use_natural_foreign_keys=True)
        else:
            custom_data = []
            for driver in drivers:
                driver_data = {
                    'model': 'your_app.driver',
                    'pk': driver.pk,
                    'fields': {
                        'driver': driver.driver_id,
                        'email': driver.email,
                        'full_name': driver.full_name,
                        'phone_number': driver.phone_number,
                        'company_name': driver.company_name,
                        'company_number': driver.company_number,
                        'digital_address': driver.digital_address,
                        'driver_code': driver.driver_code,
                    }
                }
                custom_data.append(driver_data)
            data = json.dumps(custom_data)
        
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        filepath = os.path.join(backup_dir, filename)
        with open(filepath, 'w') as f:
            f.write(data)
        
        return filepath
    
    @classmethod
    def import_from_json(cls, filename, clear_existing=False, skip_duplicates=False, 
                        update_existing=False, skip_missing_users=False):
        """Import drivers from JSON file"""
        filepath = os.path.join(settings.BASE_DIR, 'backups', filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Backup file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            data = f.read()
        
        if clear_existing:
            cls.objects.all().delete()
        
        count = 0
        updated = 0
        skipped = 0
        missing_users = 0
        with transaction.atomic():
            for obj in deserialize('json', data):
                driver_data = obj.object
                
                # Check if user exists
                try:
                    user = User.objects.get(pk=driver_data.driver_id)
                except User.DoesNotExist:
                    if skip_missing_users:
                        missing_users += 1
                        continue
                    else:
                        raise ValueError(f"User with ID {driver_data.driver_id} does not exist")
                
                # Check for existing driver by user
                existing_driver = cls.objects.filter(driver=user).first()
                
                if existing_driver:
                    if skip_duplicates:
                        skipped += 1
                        continue
                    elif update_existing:
                        # Update existing driver
                        existing_driver.email = driver_data.email
                        existing_driver.full_name = driver_data.full_name
                        existing_driver.phone_number = driver_data.phone_number
                        existing_driver.company_name = driver_data.company_name
                        existing_driver.company_number = driver_data.company_number
                        existing_driver.digital_address = driver_data.digital_address
                        existing_driver.driver_code = driver_data.driver_code
                        existing_driver.save()
                        updated += 1
                        continue
                
                obj.save()
                count += 1
        
        return count, updated, skipped, missing_users
    
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
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
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
    
    @classmethod
    def export_to_json(cls, filename=None, include_related=False, include_images=False):
        """Export all customers to JSON file"""
        if not filename:
            filename = f'customers_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        customers = cls.objects.all().select_related('customer', 'agent', 'mobilization', 'branch')
        
        if include_related:
            data = serialize('json', customers, use_natural_foreign_keys=True)
        else:
            custom_data = []
            for customer in customers:
                customer_data = {
                    'model': 'your_app.customer',
                    'pk': customer.pk,
                    'fields': {
                        'customer': customer.customer_id,
                        'agent': customer.agent_id if customer.agent else None,
                        'mobilization': customer.mobilization_id if customer.mobilization else None,
                        'branch': customer.branch_id if customer.branch else None,
                        'phone_number': customer.phone_number,
                        'full_name': customer.full_name,
                        'customer_location': customer.customer_location,
                        'digital_address': customer.digital_address,
                        'id_type': customer.id_type,
                        'id_number': customer.id_number,
                        'date_of_birth': customer.date_of_birth.isoformat() if customer.date_of_birth else None,
                        'customer_picture': cls._handle_image_export(customer.customer_picture, include_images),
                        'customer_image': cls._handle_image_export(customer.customer_image, include_images),
                        'date_created': customer.date_created.isoformat() if customer.date_created else None,
                    }
                }
                custom_data.append(customer_data)
            data = json.dumps(custom_data)
        
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        filepath = os.path.join(backup_dir, filename)
        with open(filepath, 'w') as f:
            f.write(data)
        
        return filepath
    
    @classmethod
    def import_from_json(cls, filename, clear_existing=False, skip_duplicates=False, 
                        update_existing=False, skip_missing_users=False, 
                        skip_missing_agents=False, skip_missing_mobilizations=False,
                        handle_images=False):
        """Import customers from JSON file"""
        filepath = os.path.join(settings.BASE_DIR, 'backups', filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Backup file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            data = f.read()
        
        if clear_existing:
            cls.objects.all().delete()
        
        count = 0
        updated = 0
        skipped = 0
        missing_users = 0
        missing_agents = 0
        missing_mobilizations = 0
        with transaction.atomic():
            for obj in deserialize('json', data):
                customer_data = obj.object
                
                # Check if user exists
                try:
                    user = User.objects.get(pk=customer_data.customer_id)
                except User.DoesNotExist:
                    if skip_missing_users:
                        missing_users += 1
                        continue
                    else:
                        raise ValueError(f"User with ID {customer_data.customer_id} does not exist")
                
                # Check if agent exists (if specified)
                agent = None
                if customer_data.agent_id:
                    try:
                        agent = Agent.objects.get(pk=customer_data.agent_id)
                    except Agent.DoesNotExist:
                        if skip_missing_agents:
                            missing_agents += 1
                            continue
                        else:
                            raise ValueError(f"Agent with ID {customer_data.agent_id} does not exist")
                
                # Check if mobilization exists (if specified)
                mobilization = None
                if customer_data.mobilization_id:
                    try:
                        mobilization = Mobilization.objects.get(pk=customer_data.mobilization_id)
                    except Mobilization.DoesNotExist:
                        if skip_missing_mobilizations:
                            missing_mobilizations += 1
                            continue
                        else:
                            raise ValueError(f"Mobilization with ID {customer_data.mobilization_id} does not exist")
                
                # Check for existing customer by user
                existing_customer = cls.objects.filter(customer=user).first()
                
                if existing_customer:
                    if skip_duplicates:
                        skipped += 1
                        continue
                    elif update_existing:
                        # Update existing customer
                        existing_customer.agent = agent
                        existing_customer.mobilization = mobilization
                        existing_customer.branch = customer_data.branch
                        existing_customer.phone_number = customer_data.phone_number
                        existing_customer.full_name = customer_data.full_name
                        existing_customer.customer_location = customer_data.customer_location
                        existing_customer.digital_address = customer_data.digital_address
                        existing_customer.id_type = customer_data.id_type
                        existing_customer.id_number = customer_data.id_number
                        existing_customer.date_of_birth = customer_data.date_of_birth
                        
                        # Handle images if specified
                        if handle_images:
                            existing_customer.customer_picture = cls._handle_image_import(customer_data.customer_picture, 'customer_pic')
                            existing_customer.customer_image = cls._handle_image_import(customer_data.customer_image, 'customer_image')
                        
                        existing_customer.save()
                        updated += 1
                        continue
                
                # Handle images for new customers if specified
                if handle_images:
                    customer_data.customer_picture = cls._handle_image_import(customer_data.customer_picture, 'customer_pic')
                    customer_data.customer_image = cls._handle_image_import(customer_data.customer_image, 'customer_image')
                
                obj.save()
                count += 1
        
        return count, updated, skipped, missing_users, missing_agents, missing_mobilizations
    
    @staticmethod
    def _handle_image_export(image_field, include_images):
        """Handle image field export"""
        if not image_field:
            return None
        
        if include_images and image_field:
            try:
                with open(image_field.path, 'rb') as image_file:
                    return base64.b64encode(image_file.read()).decode('utf-8')
            except (FileNotFoundError, ValueError):
                return None
        else:
            return image_field.name if image_field else None
    
    @staticmethod
    def _handle_image_import(image_data, upload_to):
        """Handle image import"""
        if not image_data:
            return None
        
        if isinstance(image_data, str) and len(image_data) > 1000:  # Likely base64
            try:
                import base64
                from django.core.files.base import ContentFile
                format, imgstr = image_data.split(';base64,') if ';base64,' in image_data else (None, image_data)
                ext = 'png' if not format else format.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr), name=f'{upload_to}_{timezone.now().timestamp()}.{ext}')
                return data
            except (ValueError, TypeError):
                return None
        return image_data
    

    
class MobilizationCustomer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mobilizationcustomer')
    mobilization = models.ForeignKey(Mobilization, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
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