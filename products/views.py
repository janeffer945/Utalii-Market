from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from django.db.models import Q
from collections import defaultdict

# Create your views here.
