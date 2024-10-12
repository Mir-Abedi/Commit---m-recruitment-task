from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
import json
from .models import User
from django.contrib.auth.hashers import make_password

@api_view(["GET"])
def all_books(request):
    pass

@api_view(["POST"])
def add_book(request):
    pass

@api_view(["POST"])
def update_book(request):
    pass

@api_view(["DELETE"])
def delete_book(request):
    pass

@api_view(["POST"])
def register_user(request):
    try:
        data = json.loads(request.body)
        name = data.get('name')
        username = data.get('username')
        email = data.get('email')
        phone_num = data.get('phone_num')
        password = data.get('password')
        is_admin = data.get('is_admin', False)

        if not all([name, username, email, password, phone_num]):
            return Response({'status': 'error', 'message': 'Missing required fields'}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({'status': 'error', 'message': 'Username already exists'}, status=400)
        if User.objects.filter(email=email).exists():
            return Response({'status': 'error', 'message': 'Email already exists'}, status=400)
        
        user = User.objects.create(
            name=name,
            username=username,
            email=email,
            phone_num=phone_num,
            password=make_password(password) 
        )
        return Response({'status': 'success', 'message': 'User registered successfully', 'user': user.username, 'user_id': user.id}, status=201)
    
    except json.JSONDecodeError:
        return Response({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
    except: 
        return Response({'status': 'error', 'message': 'Internal server error'}, status=500)

@api_view(["POST"])
def login_user(request):
    pass

@api_view(["POST"])
def borrow_book(request, book_pk):
    pass

@api_view(["POST"])
def return_book(request, book_pk):
    pass

@api_view(["POST"])
def update_user(request):
    pass