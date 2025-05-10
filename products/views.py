from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from django.db.models import Q
from collections import defaultdict

# Create your views here.
class RecommendProductView(APIView):
    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "User not authenticated"},
            status=status.HTTP_401_UNAUTHORIZED)
        
        history = BrowsingHistory.objects.filter(user=user)[:5]
        viewed_product_ids = [h.product.id for h in history]
        viewed_categories = [h.product.category for h in history]
        viewed_tags = []
        for h in history:
            viewed_tags.extend(h.product.tags.split(',')) 

        scores = defaultdict(float)
        for product in Product.objects.exclude(id__in=viewed_product_ids):
            score = 0
            if product.category in viewed_categories:
                score += 2  # Weight for category match
            product_tags = product.tags.split(',')
            for tag in product_tags:
                if tag in viewed_tags:
                    score += 1  # Weight for each tag match
            scores[product] = score  

        
        # Get top 3 products
        recommended = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
        recommended_products = [
            {"id": p.id, "name": p.name, "category": p.category, "price": str(p.price), "tags": p.tags}
            for p, _ in recommended
        ]

        return Response({"recommended": recommended_products}, status=status.HTTP_200_OK)          

        
