from django.core.management.base import BaseCommand
from django.db import transaction
from products.models import Product

class Command(BaseCommand):
    help = 'Populates the database with mock products'

    def handle(self, *args, **kwargs):
        products = [
            {"id": 1, "name": "Wireless Headphones", "category": "Electronics", "price": 99.99, "tags": "Bluetooth,Wireless,Audio"},
            {"id": 2, "name": "Smartphone", "category": "Electronics", "price": 599.99, "tags": "Bluetooth,Touchscreen"},
            {"id": 3, "name": "Laptop", "category": "Electronics", "price": 999.99, "tags": "Portable,Wireless"},
            {"id": 4, "name": "Running Shoes", "category": "Sportswear", "price": 79.99, "tags": "Athletic,Comfortable"},
            {"id": 5, "name": "Yoga Mat", "category": "Sportswear", "price": 29.99, "tags": "Fitness,Non-slip"},
            {"id": 6, "name": "Coffee Maker", "category": "Home Appliances", "price": 49.99, "tags": "Kitchen,Automatic"},
            {"id": 7, "name": "Blender", "category": "Home Appliances", "price": 39.99, "tags": "Kitchen,Blending"},
            {"id": 8, "name": "Smart Watch", "category": "Electronics", "price": 199.99, "tags": "Bluetooth,Fitness"},
            {"id": 9, "name": "Tennis Racket", "category": "Sportswear", "price": 89.99, "tags": "Athletic,Tennis"},
            {"id": 10, "name": "Microwave Oven", "category": "Home Appliances", "price": 129.99, "tags": "Kitchen,Heating"},
        ]

        with transaction.atomic():
            for product_data in products:
                Product.objects.update_or_create(
                    id=product_data['id'],
                    defaults={
                        'name': product_data['name'],
                        'category': product_data['category'],
                        'price': product_data['price'],
                        'tags': product_data['tags']
                    }
                )
        self.stdout.write(self.style.SUCCESS('Successfully populated products'))