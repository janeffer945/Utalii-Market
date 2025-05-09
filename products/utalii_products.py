from django.core.management.base import BaseCommand
from products.models import Product

class Command(BaseCommand):
    help = 'populates the database with mock products'


    def handle(self, *args, **kwargs):
        products = [
             {"name": "Wireless Headphones", "category": "Electronics", "price": 99.99, "tags": "Bluetooth,Wireless,Audio"},
            {"name": "Smartphone", "category": "Electronics", "price": 599.99, "tags": "Bluetooth,Touchscreen"},
            {"name": "Laptop", "category": "Electronics", "price": 999.99, "tags": "Portable,Wireless"},
            {"name": "Running Shoes", "category": "Sportswear", "price": 79.99, "tags": "Athletic,Comfortable"},
            {"name": "Yoga Mat", "category": "Sportswear", "price": 29.99, "tags": "Fitness,Non-slip"},
            {"name": "Coffee Maker", "category": "Home Appliances", "price": 49.99, "tags": "Kitchen,Automatic"},
            {"name": "Blender", "category": "Home Appliances", "price": 39.99, "tags": "Kitchen,Blending"},
            {"name": "Smart Watch", "category": "Electronics", "price": 199.99, "tags": "Bluetooth,Fitness"},
            {"name": "Tennis Racket", "category": "Sportswear", "price": 89.99, "tags": "Athletic,Tennis"},
            {"name": "Microwave Oven", "category": "Home Appliances", "price": 129.99, "tags": "Kitchen,Heating"},

        ]
        for product_data in products:
            Product.objects.get_or_create(**product_data)
        self.stdout.write(self.style.SUCCESS('Successfully populated products'))