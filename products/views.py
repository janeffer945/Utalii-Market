from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Product, BrowsingHistory, RecommendationClick
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

@ensure_csrf_cookie
@api_view(['GET'])
def get_csrf_token(request):
    """Return CSRF token for frontend."""
    return Response({'status': 'success'})

def mock_openai_generate_message(categories, tags):
    """Mock OpenAI API to generate a personalized recommendation message."""
    primary_category = max(set(categories), key=categories.count) if categories else "products"
    primary_tag = max(set(tags), key=tags.count) if tags else "great items"
    templates = [
        f"Since you love {primary_category.lower()} products, check out these recommendations!",
        f"Based on your interest in {primary_tag.lower()} items, you might like these too!",
        f"Explore more {primary_category.lower()} with {primary_tag.lower()} features!"
    ]
    return np.random.choice(templates)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_products(request):
    """API to fetch all products."""
    products = Product.objects.all()
    data = [{
        'id': product.id,
        'name': product.name,
        'category': product.category,
        'price': str(product.price),
        'tags': product.tags
    } for product in products]
    return Response({'products': data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_browsing_history(request):
    #save's a product view to browsing history."""
    try:
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'detail': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        product = Product.objects.get(id=product_id)
        BrowsingHistory.objects.create(user=request.user, product=product)
        return Response({'status': 'success'})
    except Product.DoesNotExist:
        return Response({'detail': 'Invalid product ID'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'detail': f'Error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_recommendation_click(request):
    #API to log a click on a recommended product
    try:
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'detail': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        product = Product.objects.get(id=product_id)
        RecommendationClick.objects.create(user=request.user, product=product)
        return Response({'status': 'success'})
    except Product.DoesNotExist:
        return Response({'detail': 'Invalid product ID'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'detail': f'Error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recommendations(request):
 #An API that return's 3 recommended products and a personalized message, with filters
    user = request.user
    min_price = request.query_params.get('min_price')
    max_price = request.query_params.get('max_price')
    category = request.query_params.get('category')

    viewed_products = BrowsingHistory.objects.filter(user=user).select_related('product')
    viewed_product_ids = [bh.product.id for bh in viewed_products]
    
    if not viewed_products:
        return Response({
            'recommendations': [],
            'message': 'Browse some products to get personalized recommendations!'
        })

    categories = [bh.product.category for bh in viewed_products]
    tags = []
    for bh in viewed_products:
        tags.extend(bh.product.tags.split(','))
    tags = [tag.strip() for tag in tags]

    all_products = Product.objects.all()
    if min_price:
        all_products = all_products.filter(price__gte=float(min_price))
    if max_price:
        all_products = all_products.filter(price__lte=float(max_price))
    if category:
        all_products = all_products.filter(category=category)
    
    product_ids = [p.id for p in all_products]
    
    if not product_ids:
        return Response({
            'recommendations': [],
            'message': 'No products match the selected filters.'
        })

    feature_strings = [
        f"{p.category} {' '.join(p.tags.split(','))}" for p in all_products
    ]
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(feature_strings)
    
    viewed_indices = [i for i, pid in enumerate(product_ids) if pid in viewed_product_ids]
    if not viewed_indices:
        return Response({
            'recommendations': [],
            'message': 'No viewed products available for recommendations.'
        })
    
    viewed_vectors = tfidf_matrix[viewed_indices]
    avg_viewed_vector = np.asarray(np.mean(viewed_vectors, axis=0))  # Convert to ndarray
    
    similarities = cosine_similarity(avg_viewed_vector, tfidf_matrix).flatten()
    
    unviewed_indices = [i for i, pid in enumerate(product_ids) if pid not in viewed_product_ids]
    unviewed_similarities = [(i, similarities[i]) for i in unviewed_indices]
    unviewed_similarities.sort(key=lambda x: x[1], reverse=True)
    top_indices = [i for i, _ in unviewed_similarities[:3]]
    
    recommended_products = [all_products[i] for i in top_indices]
    data = [{
        'id': product.id,
        'name': product.name,
        'category': product.category,
        'price': str(product.price),
        'tags': product.tags
    } for product in recommended_products]
    
    message = mock_openai_generate_message(categories, tags)
    
    return Response({
        'recommendations': data,
        'message': message
    })