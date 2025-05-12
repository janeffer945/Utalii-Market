# Utalii Marktplace Project
## Description
 A web-based Marktplace with a product recommendation system built using Django(Backend) and AngularJs (Fronted).

## Author
Janeffer Njeri: https://github.com/janeffer945  

## Setup Instructions
## Prerequisites
python3.8+
Node.Js 
Git 

## Installation
pip install Django
django-admin startproject marktplace (.)
django-admin startapp products

## Clone the Project
https://github.com/janeffer945/Utalii-Market.git



## Setup Virtual Environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

## Install Dependencies:
pip install -r requirements.txt

## Apply Migrations:
python manage.py makemigrations
python manage.py migrate

## Mock Data:
python manage.py populate_products

## Run Django Server
python manage.py runserver

## Serve the frontend:
## Utalii Market 
Installation

ng new utalii_market
## Run AngularJs Project
ng Serve

## Test the Apllication:
 Create a user via Django admin (python manage.py createsuperuser and access /admin).
 Log in and browse products at http://localhost:8000/static/index.html.
Click "ViewS" on products, apply filters, and click recommendations to test functionality.

## recommendation Approach
The recommendation system is content-based, using cosine similarity to suggest products based on user browsing history:
## Feature Extraction:
Each product is represented by its category and tags (e.g., "Electronics Bluetooth Touchscreen").
## TF-IDF Vectorization:
Converts product features into vectors using TfidfVectorizer from scikit-learn, emphasizing rare terms.
## Similarity Calculation:
 Computes the average TF-IDF vector of viewed products and compares it to all products using cosine similarity.
#Filtering: 
Supports filters for price range (min/max) and category, applied before similarity ranking.
## Personalized Message:
 A mock OpenAI function generates messages based on the most frequent category or tag (e.g., "Based on your interest in Bluetooth items, you might like these too!").
## Logging: 
Tracks recommendation clicks in the RecommendationClick model for analytics.

The system recommends 3 unviewed products, prioritizing those most similar to the user's browsing history.

## Project structure 
marketplace-project/
├── marketplace/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── management/
│   │   ├── __init__.py
│   │   └── commands/
│   │       ├── __init__.py
│   │       └── seed_data.py
│   └── migrations/
│       ├── __init__.py
│       └── (generated migration files)
├── static/
│   └── index.html
├── project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
└── README.md



## Usage
Browse products and click "View" to log browsing history.
Use filters (price range, category) to refine recommendations.
Click recommended products to log clicks, tracked in the backend.
View recommendations and personalized messages in the dedicated section.
For issues or contributions, open a pull request or issue on the GitHub repository.

