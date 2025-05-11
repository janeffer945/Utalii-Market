from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Product, BrowsingHistory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
# Create your views here.

def mock_openai_generate_message(categories, tags):
    primary_category = max(set(categories), key=categories.count) if categories else "products"
    primary_tag = max(set(tags), key=tags.count) if tags else "great items"
    templates = [
        f"Since you love{primary_category.lower()} Products, check out these recommendations!",
        f"Based on your interest in {primary_tag.lower()} items, you might like these too!",
        f"Explore more {primary_category.lower()} with {primary_tag.lower()} features!"

    ]
    return np.random.choice(templates)
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

        
class ViewProduct(APIView):
    def post(self, request):
        user = request.user
        product_id = request.data.get('product_id')
        if not user.is_authenticated:
            return Response({"error": "User is not authenticated"}),
            status-status.HTTP_401_UNAUTHORIZED
        try:
            product = Product.objects.get(id=product_id)
            BrowsingHistory.objects.create(user=user, product=product)
            return Response({"message": "Product view recorded"}, status=status.HTTP_201_CREATED)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

class BrowsingHistoryView(APIView):
    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response ({"error": "User not authenticated"}),
        history = BrowsingHistory.objects.filter(user=user)[:5]
        serializer = BrowsingHistorySerializer(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK) 
