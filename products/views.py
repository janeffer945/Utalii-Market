from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Product, BrowsingHistory, RecommendationClick
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import ensure_csrf_cookie
import json
import random

# Create your views here.
@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'status': 'success'})
# Recommendation message
def mock_openai_generate_message(categories, tags):
    primary_category = max(set(categories), key=categories.count) if categories else "products"
    primary_tag = max(set(tags), key=tags.count) if tags else "great items"
    templates = [
        f"Since you love{primary_category.lower()} Products, check out these recommendations!",
        f"Based on your interest in {primary_tag.lower()} items, you might like these too!",
        f"Explore more {primary_category.lower()} with {primary_tag.lower()} features!"

    ]
    return np.random.choice(templates)

@login_required
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
    return JsonResponse({'products': data})

#API savs product view to browsing history
@login_required
def save_browsing_history(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("method not allowed")
    
    try: 
        product_id = request.POST.GET('product_id')
        if not product_id:
            return HttpResponseBadRequest("product ID is required")

        product = product.objects.get(id=product_id) 
        BrowsingHistory.objects.create(user=request.user, product=product)
        return JsonResponse({'status': 'success'})
    except Product.DoesNotExist:
        return HttpResponseBadRequest("Invalid product ID")
    except Exception as e:
        return HttpResponseBadRequest(f"Error: {str(e)}")
    
@login_required
def log_recommendation_click(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("method not allowed")
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        if not product_id:
            return HttpResponseBadRequest("Product ID is required")

        product = Product.objects.get(id=product_id)
        RecommendationClick.objects.create(user=request.user, product=product)
        return JsonResponse({'status': 'success'})
    except Product.DoesNotExist:
        return HttpResponseBadRequest("Invalid product ID")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")
    except Exception as e:
        return HttpResponseBadRequest(f"Error: {str(e)}")  
    
#API that returns 3recommended products
@login_required
def get_recommendations(request):
    user = request.user
    #user browsing history
    viewed_products = BrowsingHistory.objects.filter(user=user).select_related('product')
    viewed_products_ids = [bh.product.id for bh in viewed_products]   

    if not viewed_products:
        return JsonResponse({'recommendations' : [],
                            'message': "Browse some products to get personalized recommendations!"  })
    
    #Extract categories from viewed products
    categories = [bh.product.category for bh in viewed_products]
    tags = []
    for bh in viewed_products:

     tags.extend(bh.product.tags.split(','))
    tags = [tag.strip() for tag in tags]  

     # Get filter parameters
    min_price = request.GET.get('min_price', None)
    max_price = request.GET.get('max_price', None)
    category = request.GET.get('category', None)

    # Get all products and apply filters
    all_products = Product.objects.all()
    if min_price:
        all_products = all_products.filter(price__gte=float(min_price))
    if max_price:
        all_products = all_products.filter(price__lte=float(max_price))
    if category:
        all_products = all_products.filter(category=category)

    product_ids = [p.id for p in all_products]

    feature_strings = [
        f"{p.category} {' '.join(p.tags.split(','))}" for p in all_products
    ]
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(feature_strings)

    viewed_indices = [i for i, pid in enumerate(product_ids) if pid in viewed_products_ids]
    viewed_vectors = tfidf_matrix(viewed_indices)
    avg_viewed_vector = np.mean(viewed_vectors, axis=0) if viewed_indices else None
    
    similarities  = cosine_similarity(avg_viewed_vector, tfidf_matrix).flatten()

    #get 3 unvewied products
    unviewed_indices = [i for i, pid in enumerate(product_ids) if pid not in viewed_products_ids]
    unviewed_similarities = [(i, similarities[i]) for i in unviewed_indices]
    unviewed_similarities.sort(key=lambda x: x[1], reverse=True)
    top_indices = [i for i, _ in unviewed_similarities[:3]]  

    recommended_products = [all_products[i] for i in top_indices
                            ]     
    data = [{
        'id' : Product.id,
        'name' : Product.name,
        'category': Product.category,
        'price' : str(Product.price),
        'tags' :Product.tags

    } for product in recommended_products]

    message = mock_openai_generate_message(categories, tags)

    return JsonResponse({
        'recommendations': data,
        'message': message
    })

    



