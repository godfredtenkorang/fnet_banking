import json
from django.core.management.base import BaseCommand
from django.core.serializers import deserialize
from models import Customer, User, Agent, Mobilization
from django.db import transaction
import os
from django.conf import settings
import base64
from django.core.files.base import ContentFile
from django.utils import timezone

class Command(BaseCommand):
    help = 'Import Customer data from JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--filename',
            type=str,
            help='Input filename (required)',
            required=True
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing data before import',
            default=False
        )
        parser.add_argument(
            '--skip-duplicates',
            action='store_true',
            help='Skip duplicate customers (by user)',
            default=False
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing customers instead of skipping',
            default=False
        )
        parser.add_argument(
            '--skip-missing-users',
            action='store_true',
            help='Skip customers with missing user references',
            default=False
        )
        parser.add_argument(
            '--skip-missing-agents',
            action='store_true',
            help='Skip customers with missing agent references',
            default=False
        )
        parser.add_argument(
            '--skip-missing-mobilizations',
            action='store_true',
            help='Skip customers with missing mobilization references',
            default=False
        )
        parser.add_argument(
            '--handle-images',
            action='store_true',
            help='Handle image data during import',
            default=False
        )

    def handle(self, *args, **options):
        filename = options['filename']
        clear_existing = options['clear_existing']
        skip_duplicates = options['skip_duplicates']
        update_existing = options['update_existing']
        skip_missing_users = options['skip_missing_users']
        skip_missing_agents = options['skip_missing_agents']
        skip_missing_mobilizations = options['skip_missing_mobilizations']
        handle_images = options['handle_images']
        
        filepath = os.path.join(settings.BASE_DIR, 'backups', filename)
        
        if not os.path.exists(filepath):
            self.stdout.write(
                self.style.ERROR(f'File not found: {filepath}')
            )
            return
        
        try:
            with open(filepath, 'r') as f:
                data = f.read()
            
            # Clear existing data if requested
            if clear_existing:
                Customer.objects.all().delete()
                self.stdout.write('Cleared existing Customer data')
            
            # Deserialize and save objects
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
                    existing_customer = Customer.objects.filter(customer=user).first()
                    
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
                                existing_customer.customer_picture = self._handle_image_import(customer_data.customer_picture, 'customer_pic')
                                existing_customer.customer_image = self._handle_image_import(customer_data.customer_image, 'customer_image')
                            
                            existing_customer.save()
                            updated += 1
                            continue
                    
                    # Handle images for new customers if specified
                    if handle_images:
                        customer_data.customer_picture = self._handle_image_import(customer_data.customer_picture, 'customer_pic')
                        customer_data.customer_image = self._handle_image_import(customer_data.customer_image, 'customer_image')
                    
                    obj.save()
                    count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully imported {count} customers, '
                    f'updated {updated}, skipped {skipped}, '
                    f'missing users: {missing_users}, '
                    f'missing agents: {missing_agents}, '
                    f'missing mobilizations: {missing_mobilizations} from {filepath}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing data: {str(e)}')
            )
    
    def _handle_image_import(self, image_data, upload_to):
        """Handle image import - decode base64 or return None"""
        if not image_data:
            return None
        
        # Check if it's base64 encoded
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            try:
                # Extract base64 data from data URL
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr), name=f'{upload_to}_{timezone.now().timestamp()}.{ext}')
                return data
            except (ValueError, TypeError):
                return None
        return image_data