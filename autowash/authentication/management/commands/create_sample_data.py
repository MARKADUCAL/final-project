from django.core.management.base import BaseCommand
from authentication.models import Service

class Command(BaseCommand):
    help = 'Creates sample services for the autowash hub'

    def handle(self, *args, **options):
        services = [
            {
                'name': 'Basic Wash',
                'description': 'Exterior wash with basic cleaning.',
                'price': 15.99,
                'duration_minutes': 30
            },
            {
                'name': 'Premium Wash',
                'description': 'Exterior wash with premium cleaning products, includes tire shine and wheel cleaning.',
                'price': 29.99,
                'duration_minutes': 45
            },
            {
                'name': 'Deluxe Package',
                'description': 'Complete interior and exterior cleaning with premium products.',
                'price': 49.99,
                'duration_minutes': 90
            },
            {
                'name': 'Interior Detail',
                'description': 'Deep cleaning of all interior surfaces, includes vacuuming and stain removal.',
                'price': 39.99,
                'duration_minutes': 60
            },
            {
                'name': 'Full Detail Package',
                'description': 'Complete detailing of both interior and exterior, includes waxing and polishing.',
                'price': 89.99,
                'duration_minutes': 180
            }
        ]
        
        created_count = 0
        for service_data in services:
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults={
                    'description': service_data['description'],
                    'price': service_data['price'],
                    'duration_minutes': service_data['duration_minutes']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created service: {service.name}'))
            else:
                self.stdout.write(f'Service already exists: {service.name}')
        
        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(f'Created {created_count} new services'))
        else:
            self.stdout.write(self.style.SUCCESS('All services already exist')) 