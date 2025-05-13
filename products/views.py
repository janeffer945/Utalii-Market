from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Product, BrowsingHistory, RecommendationClick
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging
import random

logger = logging.getLogger(__name__)

@ensure_csrf_cookie
@api_view(['GET'])
def get_csrf_token(request):
    return Response({'status': 'success'})

def mock_openai_generate_message(categories, tags, is_fallback=False):
    if is_fallback:
        return "Check out these popular products!"
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
    products = Product.objects.all()
    data = [{
        'id': product.id,
        'name': product.name,
        'category': product.category,
        'price': float(product.price),
        'tags': product.tags
    } for product in products]
    return Response({'products': data})

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def browsing_history(request):
    if request.method == 'POST':
        try:
            product_id = request.data.get('product_id')
            if not product_id:
                return Response({'detail': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            product = Product.objects.get(id=product_id)
            if not BrowsingHistory.objects.filter(user=request.user, product=product).exists():
                BrowsingHistory.objects.create(user=request.user, product=product)
                logger.debug(f"Created browsing history for user {request.user.username}, product {product.name}")
            else:
                logger.debug(f"Browsing history already exists for user {request.user.username}, product {product.name}")
            return Response({'status': 'success'})
        except Product.DoesNotExist:
            return Response({'detail': 'Invalid product ID'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': f'Error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'GET':
        try:
            history = BrowsingHistory.objects.filter(user=request.user).select_related('product').order_by('-viewed_at')
            data = [{
                'id': entry.id,
                'product_name': entry.product.name,
                'category': entry.product.category,
                'price': float(entry.product.price),
                'tags': entry.product.tags,
                'viewed_at': entry.viewed_at.isoformat()
            } for entry in history]
            return Response({'history': data})
        except Exception as e:
            logger.error(f"Error in get_browsing_history: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_recommendation_click(request):
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
def get_recommendation_clicks(request):
    try:
        clicks = RecommendationClick.objects.filter(user=request.user).select_related('product').order_by('-timestamp')
        data = [{
            'id': click.id,
            'product_name': click.product.name,
            'category': click.product.category,
            'price': float(click.product.price),
            'tags': click.product.tags,
            'timestamp': click.timestamp.isoformat()
        } for click in clicks]
        return Response({'clicks': data})
    except Exception as e:
        logger.error(f"Error in get_recommendation_clicks: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_browsing_history(request):
    try:
        history = BrowsingHistory.objects.filter(user=request.user).select_related('product').order_by('-viewed_at')
        data = [{
            'id': entry.id,
            'product_name': entry.product.name,
            'category': entry.product.category,
            'price': float(entry.product.price),
            'tags': entry.product.tags,
            'viewed_at': entry.viewed_at.isoformat()
        } for entry in history]
        return Response({'history': data})
    except Exception as e:
        logger.error(f"Error in get_browsing_history: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recommendations(request):
    try:
        user = request.user
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        category = request.query_params.get('category')

        logger.debug(f"User: {user.username}, Filters: min_price={min_price}, max_price={max_price}, category={category}")

        viewed_products = BrowsingHistory.objects.filter(user=user).select_related('product')
        viewed_product_ids = [bh.product.id for bh in viewed_products]

        unique_viewed = {}
        for bh in viewed_products:
            if bh.product.id not in unique_viewed:
                unique_viewed[bh.product.id] = bh
        viewed_data = [{
            'id': bh.product.id,
            'name': bh.product.name,
            'category': bh.product.category,
            'price': float(bh.product.price),
            'tags': bh.product.tags
        } for bh in unique_viewed.values()]

        categories = [bh.product.category for bh in viewed_products]
        tags = [tag.strip() for bh in viewed_products for tag in bh.product.tags.split(',')]

        all_products = Product.objects.all()
        filtered_products = all_products
        if min_price:
            filtered_products = filtered_products.filter(price__gte=float(min_price))
        if max_price:
            filtered_products = filtered_products.filter(price__lte=float(max_price))
        if category:
            filtered_products = filtered_products.filter(category=category)

        product_ids = [p.id for p in filtered_products]
        unviewed_products = filtered_products.exclude(id__in=viewed_product_ids)

        unviewed_data = [{
            'id': p.id,
            'name': p.name,
            'category': p.category,
            'price': float(p.price),
            'tags': p.tags
        } for p in unviewed_products]

        recommendations = []
        message = None

        if viewed_products and unviewed_products.exists():
            feature_strings = [f"{p.category} {' '.join(p.tags.split(','))}" for p in filtered_products]
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(feature_strings)

            viewed_indices = [i for i, pid in enumerate(product_ids) if pid in viewed_product_ids]
            
            if viewed_indices:
                viewed_vectors = tfidf_matrix[viewed_indices]
                avg_viewed_vector = np.asarray(np.mean(viewed_vectors, axis=0))
                similarities = cosine_similarity(avg_viewed_vector, tfidf_matrix).flatten()

                unviewed_indices = [i for i, pid in enumerate(product_ids) if pid not in viewed_product_ids]
                unviewed_similarities = [(i, similarities[i]) for i in unviewed_indices]
                unviewed_similarities.sort(key=lambda x: x[1], reverse=True)
                top_indices = [i for i, _ in unviewed_similarities[:3]]

                recommendations = [filtered_products[i] for i in top_indices]
                message = mock_openai_generate_message(categories, tags)

        if len(recommendations) < 3:
            logger.debug("Falling back to random products due to insufficient personalized recommendations")
            fallback_products = list(all_products.order_by('?')[:3 - len(recommendations)])
            recommendations.extend(fallback_products)
            if not message:
                message = mock_openai_generate_message(categories, tags, is_fallback=True)

        recommendations_data = [{
            'id': product.id,
            'name': product.name,
            'category': product.category,
            'price': float(product.price),
            'tags': product.tags
        } for product in recommendations]

        return Response({
            'recommendations': recommendations_data,
            'viewed_products': viewed_data,
            'unviewed_products': unviewed_data,
            'message': message
        })
    except Exception as e:
        logger.error(f"Error in get_recommendations: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)