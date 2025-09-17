from django.db import models
from users.models import User, Mobilization
from django.utils import timezone
from django.db.models import Sum
from users.models import MobilizationCustomer, Customer
from PIL import Image
from banking.models import MobilizationAccount
from django.core.validators import MinValueValidator

import os
from django.conf import settings
from django.core.serializers import serialize, deserialize
from django.db import transaction
from django.core.files.base import ContentFile
from decimal import Decimal
import base64
import json


REQUEST_STATUS = (
    ("Pending", "Pending"),
    ("Approved", "Approved"),
    ("Rejected", "Rejected")
)

# Create your models here.

class MobilizationPayTo(models.Model):
    PAY_TO_DEPOSIT_TYPE = (
        ("Agent", "Agent"),
        ("Merchant", "Merchant"),
    )

    NETWORKS = (
        ("Mtn", "Mtn"),
        ("Telecel", "Telecel"),
        ("AirtelTigo", "AirtelTigo"),
    )

    REQUEST_STATUS = (
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected")
    )
    mobilization = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mobilization_pay_to")
    agent_number = models.CharField(max_length=10, blank=True)
    network = models.CharField(max_length=20, choices=NETWORKS, blank=True, default="Select Network")
    # customer_name = models.CharField(max_length=30, blank=True)
    deposit_type = models.CharField(max_length=20, blank=True, choices=PAY_TO_DEPOSIT_TYPE)
    sent_to_agent_number = models.CharField(max_length=30, blank=True, default="")
    merchant_code = models.CharField(max_length=30, blank=True, default="")
    merchant_number = models.CharField(max_length=30, blank=True, default="")
    amount = models.DecimalField(max_digits=19, decimal_places=2, blank=True)
    reference = models.CharField(max_length=100, blank=True, default="")
    # charges = models.DecimalField(max_digits=19, decimal_places=2, default=0.0)
    # agent_commission = models.DecimalField(max_digits=19, decimal_places=2, default=0.0)
    date_deposited = models.DateField(auto_now_add=True)
    time_deposited = models.TimeField(auto_now_add=True)
    
    @classmethod
    def total_cash_for_customer(cls, mobilization):
        total = cls.objects.filter(mobilization=mobilization).aggregate(Sum('amount'))
        return total['amount__sum'] or 0
    
    # def save(self, *args, **kwargs):
    #     commission_amount = self.cash_received - self.amount
        
    #     # Save the CustomerCashIn instance
    #     super().save(*args, **kwargs)
        
    #     CashInCommission.objects.update_or_create(
    #         customer_cash_in=self, defaults={'amount': commission_amount} 
    #     )

    def __str__(self):
        return f"Pay To of GH¢{self.amount} on {self.network} by {self.mobilization.phone_number}"
    
    
class BankDeposit(models.Model):
    mobilization = models.ForeignKey(Mobilization, on_delete=models.CASCADE, related_name='bank_deposits')
    phone_number = models.CharField(max_length=10)
    bank = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    account_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0.01)])
    receipt = models.ImageField(upload_to='receipt_img/', null=True, blank=True)
    # mobilization_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    owner_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    screenshot = models.ImageField(upload_to='screenshot_img/', null=True, blank=True)
    screenshot2 = models.ImageField(upload_to='screenshot_img2/', null=True, blank=True)
    screenshot3 = models.ImageField(upload_to='screenshot_img3/', null=True, blank=True)
    screenshot4 = models.ImageField(upload_to='screenshot_img4/', null=True, blank=True)
    screenshot5 = models.ImageField(upload_to='screenshot_img5/', null=True, blank=True)
    screenshot6 = models.ImageField(upload_to='screenshot_img6/', null=True, blank=True)
    screenshot7 = models.ImageField(upload_to='screenshot_img7/', null=True, blank=True)
    screenshot8 = models.ImageField(upload_to='screenshot_img8/', null=True, blank=True)
    screenshot9 = models.ImageField(upload_to='screenshot_img9/', null=True, blank=True)
    screenshot10 = models.ImageField(upload_to='screenshot_img10/', null=True, blank=True)
    status = models.CharField(max_length=100, choices=REQUEST_STATUS, default='Pending')
    date_deposited = models.DateField(default=timezone.now)
    time_deposited = models.TimeField(default=timezone.now)
    
    @classmethod
    def total_bank_deposit_for_customer(cls, mobilization, status):
        total = cls.objects.filter(mobilization=mobilization, status=status).aggregate(Sum('amount'))
        return total['amount__sum'] or 0
        
    class Meta:
        ordering = ['-date_deposited']
    
    def __str__(self):
        return f"Bank Deposit of GH¢{self.amount} to {self.bank} by {self.phone_number} ({self.status})"
    
    @classmethod
    def export_to_json(cls, filename=None, include_related=False, include_images=False):
        """Export all bank deposits to JSON file"""
        if not filename:
            filename = f'bank_deposits_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        deposits = cls.objects.all().select_related('mobilization')
        
        if include_related:
            data = serialize('json', deposits, use_natural_foreign_keys=True)
        else:
            custom_data = []
            for deposit in deposits:
                deposit_data = {
                    'model': 'your_app.bankdeposit',
                    'pk': deposit.pk,
                    'fields': {
                        'mobilization': deposit.mobilization_id if deposit.mobilization else None,
                        'phone_number': deposit.phone_number,
                        'bank': deposit.bank,
                        'account_number': deposit.account_number,
                        'account_name': deposit.account_name,
                        'amount': str(deposit.amount),
                        'receipt': cls._handle_image_export(deposit.receipt, include_images),
                        'owner_transaction_id': deposit.owner_transaction_id,
                        'screenshot': cls._handle_image_export(deposit.screenshot, include_images),
                        'screenshot2': cls._handle_image_export(deposit.screenshot2, include_images),
                        'screenshot3': cls._handle_image_export(deposit.screenshot3, include_images),
                        'screenshot4': cls._handle_image_export(deposit.screenshot4, include_images),
                        'screenshot5': cls._handle_image_export(deposit.screenshot5, include_images),
                        'screenshot6': cls._handle_image_export(deposit.screenshot6, include_images),
                        'screenshot7': cls._handle_image_export(deposit.screenshot7, include_images),
                        'screenshot8': cls._handle_image_export(deposit.screenshot8, include_images),
                        'screenshot9': cls._handle_image_export(deposit.screenshot9, include_images),
                        'screenshot10': cls._handle_image_export(deposit.screenshot10, include_images),
                        'status': deposit.status,
                        'date_deposited': deposit.date_deposited.isoformat() if deposit.date_deposited else None,
                        'time_deposited': deposit.time_deposited.isoformat() if deposit.time_deposited else None,
                    }
                }
                custom_data.append(deposit_data)
            data = json.dumps(custom_data)
        
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        filepath = os.path.join(backup_dir, filename)
        with open(filepath, 'w') as f:
            f.write(data)
        
        return filepath
    
    @classmethod
    def import_from_json(cls, filename, clear_existing=False, skip_missing_mobilizations=False, 
                        handle_images=False, skip_duplicates=False):
        """Import bank deposits from JSON file"""
        filepath = os.path.join(settings.BASE_DIR, 'backups', filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Backup file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            data = f.read()
        
        if clear_existing:
            cls.objects.all().delete()
        
        count = 0
        skipped = 0
        missing_mobilizations = 0
        with transaction.atomic():
            for obj in deserialize('json', data):
                deposit_data = obj.object
                
                # Check if mobilization exists (if specified)
                mobilization = None
                if deposit_data.mobilization_id:
                    try:
                        mobilization = Mobilization.objects.get(pk=deposit_data.mobilization_id)
                    except Mobilization.DoesNotExist:
                        if skip_missing_mobilizations:
                            missing_mobilizations += 1
                            continue
                        else:
                            raise ValueError(f"Mobilization with ID {deposit_data.mobilization_id} does not exist")
                
                # Check for duplicates
                if skip_duplicates:
                    if deposit_data.owner_transaction_id:
                        existing_deposit = cls.objects.filter(
                            owner_transaction_id=deposit_data.owner_transaction_id
                        ).first()
                        if existing_deposit:
                            skipped += 1
                            continue
                    
                    existing_deposit = cls.objects.filter(
                        bank=deposit_data.bank,
                        account_number=deposit_data.account_number,
                        amount=deposit_data.amount,
                        date_deposited=deposit_data.date_deposited
                    ).first()
                    if existing_deposit:
                        skipped += 1
                        continue
                
                # Handle amount conversion
                if isinstance(deposit_data.amount, str):
                    try:
                        deposit_data.amount = Decimal(deposit_data.amount)
                    except (ValueError, TypeError):
                        deposit_data.amount = Decimal('0.00')
                
                # Handle images if specified
                if handle_images:
                    deposit_data.receipt = cls._handle_image_import(deposit_data.receipt, 'receipt_img')
                    deposit_data.screenshot = cls._handle_image_import(deposit_data.screenshot, 'screenshot_img')
                    deposit_data.screenshot2 = cls._handle_image_import(deposit_data.screenshot2, 'screenshot_img2')
                    deposit_data.screenshot3 = cls._handle_image_import(deposit_data.screenshot3, 'screenshot_img3')
                    deposit_data.screenshot4 = cls._handle_image_import(deposit_data.screenshot4, 'screenshot_img4')
                    deposit_data.screenshot5 = cls._handle_image_import(deposit_data.screenshot5, 'screenshot_img5')
                    deposit_data.screenshot6 = cls._handle_image_import(deposit_data.screenshot6, 'screenshot_img6')
                    deposit_data.screenshot7 = cls._handle_image_import(deposit_data.screenshot7, 'screenshot_img7')
                    deposit_data.screenshot8 = cls._handle_image_import(deposit_data.screenshot8, 'screenshot_img8')
                    deposit_data.screenshot9 = cls._handle_image_import(deposit_data.screenshot9, 'screenshot_img9')
                    deposit_data.screenshot10 = cls._handle_image_import(deposit_data.screenshot10, 'screenshot_img10')
                
                obj.save()
                count += 1
        
        return count, skipped, missing_mobilizations
    
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
        
        if isinstance(image_data, str) and len(image_data) > 100:  # Likely base64
            try:
                import base64
                from django.core.files.base import ContentFile
                
                if ';base64,' in image_data:
                    format, imgstr = image_data.split(';base64,')
                    ext = format.split('/')[-1]
                else:
                    imgstr = image_data
                    ext = 'png'
                
                data = ContentFile(base64.b64decode(imgstr), name=f'{upload_to}_{timezone.now().timestamp()}.{ext}')
                return data
            except (ValueError, TypeError):
                return None
        return image_data
    
class BankWithdrawal(models.Model):
    mobilization = models.ForeignKey(Mobilization, on_delete=models.CASCADE, related_name='bank_withdrawals')
    customer_phone = models.CharField(max_length=15)
    bank = models.CharField(max_length=20)
    account_number = models.CharField(max_length=20)
    account_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2, )
    ghana_card = models.ImageField(upload_to='ghana_card_img/', default='', null=True, blank=True)
    date_withdrawn = models.DateField(default=timezone.now)
    time_withdrawn = models.TimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=REQUEST_STATUS, default='Pending')
    
    @classmethod
    def total_bank_withdrawal_for_customer(cls, mobilization):
        total = cls.objects.filter(mobilization=mobilization).aggregate(Sum('amount'))
        return total['amount__sum'] or 0
    
    
    class Meta:
        ordering = ['-date_withdrawn']
    
    def __str__(self):
        return f"Bank Withdrawal of GH¢{self.amount} from {self.bank} by {self.customer_phone} ({self.status})"
    

class PaymentRequest(models.Model):
    MODE_OF_PAYMENT = [
        ('Telco', 'Telco'),
        ('Bank', 'Bank'),
        ('Branch', 'Branch'),
    ]
    
    BANK_CHOICES = [
        ("Select bank", "Select bank"),
        ("Ecobank", "Ecobank"),
        ("Access Bank", "Access Bank"),
        ("Cal Bank", "Cal Bank"),
        ("Fidelity Bank", "Fidelity Bank"),
        ("GT Bank", "GT Bank"),
        ("UBA", "UBA"),
        ("Prudential Bank", "Prudential Bank"),
        ("Adansi rural bank", "Adansi rural bank"),
        ("Kwumawuman Bank", "Kwumawuman Bank"),
        ("Pan Africa", "Pan Africa"),
        ("SGSSB", "SGSSB"),
        ("Atwima Rural Bank", "Atwima Rural Bank"),
        ("Omnibsic Bank", "Omnibsic Bank"),
        ("Omini bank", "Omini bank"),
        ("Stanbic Bank", "Stanbic Bank"),
        ("First Bank of Nigeria", "First Bank of Nigeria"),
        ("Adehyeman Savings and loans", "Adehyeman Savings and loans",),
        ("ARB Apex Bank Limited", "ARB Apex Bank Limited",),
        ("Absa Bank", "Absa Bank"),
        ("Agriculture Development bank", "Agriculture Development bank"),
        ("Bank of Africa", "Bank of Africa"),
        ("Bank of Ghana", "Bank of Ghana"),
        ("Consolidated Bank Ghana", "Consolidated Bank Ghana"),
        ("First Atlantic Bank", "First Atlantic Bank"),
        ("First National Bank", "First National Bank"),
        ("G-Money", "G-Money"),
        ("GCB BanK LTD", "GCB BanK LTD"),
        ("Ghana Pay", "Ghana Pay"),
        ("GHL Bank Ltd", "GHL Bank Ltd"),
        ("National Investment Bank", "National Investment Bank"),
        ("Opportunity International Savings And Loans", "Opportunity International Savings And Loans"),
        ("Prudential Bank", "Prudential Bank"),
        ("Republic Bank Ltd", "Republic Bank Ltd"),
        ("Sahel Sahara Bank", "Sahel Sahara Bank"),
        ("Sinapi Aba Savings and Loans", "Sinapi Aba Savings and Loans"),
        ("Societe Generale Ghana Ltd", "Societe Generale Ghana Ltd"),
        ("Standard Chartered", "Standard Chartered"),
        ("universal Merchant Bank", "universal Merchant Bank"),
        ("Zenith Bank", "Zenith Bank"),
        ("Mtn", "Mtn"),
        ("AirtelTigo", "AirtelTigo"),
        ("Telecel", "Telecel"),
    ]

    NETWORK_CHOICES = [
        ('Select Network', 'Select Network'),
        ('MTN', 'MTN'),
        ('Telecel', 'Telecel'),
        ('AirtelTigo', 'AirtelTigo'),
    ]
    
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
    )
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    mobilization = models.ForeignKey(Mobilization, on_delete=models.CASCADE, related_name='payments_requests')
    mode_of_payment = models.CharField(max_length=10, choices=MODE_OF_PAYMENT, null=True, blank=True)
    bank = models.CharField(max_length=50, choices=BANK_CHOICES, null= True, blank=True)
    network = models.CharField(max_length=30, choices=NETWORK_CHOICES, null= True, blank=True)
    branch = models.CharField(max_length=30, choices=BRANCHES, null= True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    mobilization_transaction_id = models.CharField(max_length=100, null=True, blank=True, unique=True)
    owner_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
    @classmethod
    def total_payment_for_customer(cls, mobilization, status):
        total = cls.objects.filter(mobilization=mobilization, status=status).aggregate(Sum('amount'))
        return total['amount__sum'] or 0
    

    
    class Meta:
        ordering = ['-created_at']
        
    
    def __str__(self):
        return f"Payment of GH¢{self.amount} via {self.mode_of_payment} by {self.mobilization.mobilization} ({self.status})"
    
    @classmethod
    def export_to_json(cls, filename=None, include_related=False):
        """Export all payment requests to JSON file"""
        if not filename:
            filename = f'payment_requests_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        payment_requests = cls.objects.all().select_related('mobilization')
        
        if include_related:
            data = serialize('json', payment_requests, use_natural_foreign_keys=True)
        else:
            custom_data = []
            for payment_request in payment_requests:
                payment_request_data = {
                    'model': 'your_app.paymentrequest',
                    'pk': payment_request.pk,
                    'fields': {
                        'mobilization': payment_request.mobilization_id if payment_request.mobilization else None,
                        'mode_of_payment': payment_request.mode_of_payment,
                        'bank': payment_request.bank,
                        'network': payment_request.network,
                        'branch': payment_request.branch,
                        'name': payment_request.name,
                        'amount': str(payment_request.amount),
                        'mobilization_transaction_id': payment_request.mobilization_transaction_id,
                        'owner_transaction_id': payment_request.owner_transaction_id,
                        'status': payment_request.status,
                        'created_at': payment_request.created_at.isoformat() if payment_request.created_at else None,
                        'updated_at': payment_request.updated_at.isoformat() if payment_request.updated_at else None,
                    }
                }
                custom_data.append(payment_request_data)
            data = json.dumps(custom_data)
        
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        filepath = os.path.join(backup_dir, filename)
        with open(filepath, 'w') as f:
            f.write(data)
        
        return filepath
    
    @classmethod
    def import_from_json(cls, filename, clear_existing=False, skip_missing_mobilizations=False, 
                        skip_duplicates=False, update_existing=False):
        """Import payment requests from JSON file"""
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
        missing_mobilizations = 0
        with transaction.atomic():
            for obj in deserialize('json', data):
                payment_request_data = obj.object
                
                # Check if mobilization exists
                mobilization = None
                if payment_request_data.mobilization_id:
                    try:
                        mobilization = Mobilization.objects.get(pk=payment_request_data.mobilization_id)
                    except Mobilization.DoesNotExist:
                        if skip_missing_mobilizations:
                            missing_mobilizations += 1
                            continue
                        else:
                            raise ValueError(f"Mobilization with ID {payment_request_data.mobilization_id} does not exist")
                
                # Handle amount conversion
                if isinstance(payment_request_data.amount, str):
                    try:
                        payment_request_data.amount = Decimal(payment_request_data.amount)
                    except (ValueError, TypeError):
                        payment_request_data.amount = Decimal('0.00')
                
                # Check for duplicates
                if skip_duplicates:
                    if payment_request_data.mobilization_transaction_id:
                        existing_request = cls.objects.filter(
                            mobilization_transaction_id=payment_request_data.mobilization_transaction_id
                        ).first()
                        if existing_request:
                            if update_existing:
                                # Update existing payment request
                                existing_request.mobilization = mobilization
                                existing_request.mode_of_payment = payment_request_data.mode_of_payment
                                existing_request.bank = payment_request_data.bank
                                existing_request.network = payment_request_data.network
                                existing_request.branch = payment_request_data.branch
                                existing_request.name = payment_request_data.name
                                existing_request.amount = payment_request_data.amount
                                existing_request.owner_transaction_id = payment_request_data.owner_transaction_id
                                existing_request.status = payment_request_data.status
                                existing_request.save()
                                updated += 1
                                continue
                            else:
                                skipped += 1
                                continue
                    
                    if payment_request_data.owner_transaction_id:
                        existing_request = cls.objects.filter(
                            owner_transaction_id=payment_request_data.owner_transaction_id
                        ).first()
                        if existing_request:
                            if update_existing:
                                # Update existing payment request
                                existing_request.mobilization = mobilization
                                existing_request.mode_of_payment = payment_request_data.mode_of_payment
                                existing_request.bank = payment_request_data.bank
                                existing_request.network = payment_request_data.network
                                existing_request.branch = payment_request_data.branch
                                existing_request.name = payment_request_data.name
                                existing_request.amount = payment_request_data.amount
                                existing_request.mobilization_transaction_id = payment_request_data.mobilization_transaction_id
                                existing_request.status = payment_request_data.status
                                existing_request.save()
                                updated += 1
                                continue
                            else:
                                skipped += 1
                                continue
                
                obj.save()
                count += 1
        
        return count, updated, skipped, missing_mobilizations
    
class CustomerAccount(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customeraccounts')
    account_number = models.CharField(max_length=16, blank=True)
    account_name = models.CharField(max_length=100, blank=True)
    bank = models.CharField(max_length=100, blank=True, default='')
    phone_number = models.CharField(max_length=15, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.account_name and self.customer:
            self.account_name = self.customer.full_name
        super().save(*args, **kwargs)
        
    
    @classmethod
    def export_to_json(cls, filename=None):
        """Export all accounts to JSON file"""
        if not filename:
            filename = f'customer_accounts_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        accounts = cls.objects.all()
        data = serialize('json', accounts)
        
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        filepath = os.path.join(backup_dir, filename)
        with open(filepath, 'w') as f:
            f.write(data)
        
        return filepath
    
    @classmethod
    def import_from_json(cls, filename, clear_existing=False):
        """Import accounts from JSON file"""
        filepath = os.path.join(settings.BASE_DIR, 'backups', filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Backup file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            data = f.read()
        
        if clear_existing:
            cls.objects.all().delete()
        
        count = 0
        with transaction.atomic():
            for obj in deserialize('json', data):
                obj.save()
                count += 1
        
        return count
    
    def __str__(self):
        return f"{self.phone_number} - {self.account_name} - {self.bank}"
    
    
class TellerCalculator(models.Model):
    mobilization = models.ForeignKey(Mobilization, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=13)
    amount = models.DecimalField(decimal_places=2, max_digits=19, default=0.0)
    d_200 = models.CharField(max_length=100, null=True, blank=True)
    d_100 = models.CharField(max_length=100, null=True, blank=True)
    d_50 = models.CharField(max_length=100, null=True, blank=True)
    d_20 = models.CharField(max_length=100, null=True, blank=True)
    d_10 = models.CharField(max_length=100, null=True, blank=True)
    d_5 = models.CharField(max_length=100, null=True, blank=True)
    d_2 = models.CharField(max_length=100, null=True, blank=True)
    d_1 = models.CharField(max_length=100, null=True, blank=True)
    date_added = models.DateField(auto_now_add=True)
    time_added = models.TimeField(auto_now_add=True)
    

        
    def __str__(self):
        return f"{self.customer_name} - Total: {self.amount}"
    

class Report(models.Model):
    mobilization = models.ForeignKey(Mobilization, on_delete=models.CASCADE)
    report = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Report from {self.mobilization.full_name}"