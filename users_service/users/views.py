from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
import json
from .models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

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

@csrf_exempt
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
            password=make_password(password),
            is_admin=is_admin
        )
        return Response({'status': 'success', 'message': 'User registered successfully', 'user': user.username, 'user_id': user.id}, status=201)
    
    except json.JSONDecodeError:
        return Response({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
    except Exception as e: 
        print(e)
        return Response({'status': 'error', 'message': 'Internal server error'}, status=500)

@csrf_exempt
@api_view(["POST"])
def login_user(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({'status': 'success', 'message': 'Logged in successfully'}, status=200)
        else:
            return Response({'status': 'error', 'message': 'Invalid credentials'}, status=400)
    except json.JSONDecodeError:
        return Response({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        print(e)
        return Response({'status': 'error', 'message': 'Invalid JSON data'}, status=400)

@api_view(["POST"])
@login_required
def logout_user(request):
    logout(request)
    return Response({'status': 'success', 'message': 'Logged out successfully'}, status=200)

@api_view(["POST"])
def borrow_book(request, book_pk):
    pass

@api_view(["POST"])
def return_book(request, book_pk):
    pass

@api_view(["PUT"])
@login_required
def update_user(request):
    try: 
        user = request.user
        data = json.loads(request.body)

        name = data.get('name')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        phone_num = data.get('phone_num')
        is_admin = data.get('is_admin')

        if not name:
            if user.name == name:
                return Response({'status': 'error', 'message': 'Name has not changed'}, status=400)
            if User.objects.filter(name=name).exists():
                return Response({'status': 'error', 'message': 'Name already exists'}, status=400)
        
        if not username:
            if user.username == username:
                return Response({'status': 'error', 'message': 'Username has not changed'}, status=400)
            if User.objects.filter(username=username).exists():
                return Response({'status': 'error', 'message': 'Username already exists'}, status=400) 
        
        if not email:
            if user.email == email:
                return Response({'status': 'error', 'message': 'Email has not changed'}, status=400)
            if User.objects.filter(email=email).exists():
                return Response({'status': 'error', 'message': 'Email already exists'}, status=400)
        
        user.name = name
        user.username = username
        user.email = email
        user.phone_num = phone_num
        user.is_admin = is_admin
        user.password = make_password(password)

        user.save()
        return Response({'status': 'success', 'message': 'Profile updated'}, status=200)

    except Exception as e:
        print(e)
        return Response({'status': 'error', 'message': 'Internal server error'}, status=500)

@api_view(["GET"])
@login_required
def me(request):
    try: 
        user = request.user
        return Response({'status': 'success', 'user_id': user.id, 'name': user.name, 'username': user.username, 
                         'email': user.email, 'phone_num': user.phone_num, 'is_admin': user.is_admin}, status=200)

    except Exception as e:
        print(e)
        return Response({'status': 'error', 'message': 'Internal server error'}, status=500)