# Utalii Marktplace Project
## Description
 A web-based Marktplace with a product recommendation system built using Django(Backend) and AngularJs (Fronted).

## Author
Janeffer Njeri: https://github.com/janeffer945  
Features
1. User authentication (login/logout). 
2. Browse products and save unique viewing history.
3. Personalized recommendations (3 products) using cosine similarity.
4. Filter recommendations by price and category.
5. View browsing history, viewed, and unviewed products.
6. Log and view clicks on recommended products.
7. Swagger API documentation (/swagger/).

## Setup Instructions
## Prerequisites
* Python 3.8+
* MySQL
* Django 4.1
* Django REST Framework
* scikit-learn
* drf-yasg
* corsheaders
* mysqlclient

## Installation
* pip install Django
* django-admin startproject marktplace (.)
* django-admin startapp products

## Clone the Project
https://github.com/janeffer945/Utalii-Market.git



## Setup Virtual Environment:
* python -m venv venv
* source venv/bin/activate 

* On Windows: venv\Scripts\activate

## Install Dependencies:
pip install -r requirements.txt

## Apply Migrations:
* python manage.py makemigrations
* python manage.py migrate

## createsuperuser
• python manage.py createsuperuser

## collectstatic
• python manage.py collectstatic


## Mock Data:
• python manage.py populate_products

## Run Django Server
• python manage.py runserver

## Serve the frontend:
1. Ensure index.html, app.js, and styles.css are in marketplace/static/.
2. lace index.html in marketplace/templates/.
3. Access the frontend at http://localhost:8000/.

## Endpoints
1. GET /api/products/: List all products.
2. POST /api/browsing-history/: Save product view ({ "product_id": 1 }).
3. GET /api/browsing-history/: List users browsing history.
4. GET /api/recommendations/: Get 3 recommendations, viewed, and unviewed products (?min_price=20&max_price=100&category=Electronics).
5. POST /api/recommendation-click/: Log recommendation click ({ "product_id": 1 }).
6. GET /api/recommendation-click/: List users recommendation clicks.
7. GET /api/get-csrf-token/: Get CSRF token.
8. POST /accounts/login/: Authenticate user.
9. POST /accounts/logout/: Log out user.

## recommendation Approach
The recommendation system is content-based, using cosine similarity to suggest products based on user browsing history: 
1. Feature Extraction:
Each product is represented by its category and tags (e.g., "Electronics Bluetooth Touchscreen").
2. TF-IDF Vectorization:
Converts product features into vectors using TfidfVectorizer from scikit-learn, emphasizing rare terms.
3. Similarity Calculation:
 Computes the average TF-IDF vector of viewed products and compares it to all products using cosine similarity.
4. Filtering: 
Supports filters for price range (min/max) and category, applied before similarity ranking.
5. Personalized Message:
 A mock OpenAI function generates messages based on the most frequent category or tag (e.g., "Based on your interest in Bluetooth items, you might like these too!").
6. Logging: 
Tracks recommendation clicks in the RecommendationClick model for analytics
The system recommends 3 unviewed products, prioritizing those most similar to the user browsing history


## Usage
• Browse products and click "View" to log browsing history.
• Use filters (price range, category) to refine recommendations.
• Click recommended products to log clicks, tracked in the backend.
• View recommendations and personalized messages in the dedicated section.
• For issues or contributions, open a pull request or issue on the GitHub repository.


