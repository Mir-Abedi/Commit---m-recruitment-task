from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
import json
from .models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import grpc
from . import books_pb2_grpc
from . import books_pb2
from . import borrow_pb2
from . import borrow_pb2_grpc

AVAILABLE_BOOK_GENRES = ["Fantasy", "Romance", "Horror", "Sci-Fi", "Thriller"]

@api_view(["GET"])
def all_books(request):
    try:
        with grpc.insecure_channel('books_service:50051') as channel:
            response = books_pb2_grpc.BooksServiceStub(channel).all_books(books_pb2.EmptyObject())
        return Response([{'title': i.title, 'author': i.author, 'genre': i.genre} for i in response.books], status=200)
    except Exception as e:
        return Response({'status': 'error', 'message': 'Internal server error'}, status=500)
        
@api_view(["POST"])
def add_book(request):
    try:
        data = json.loads(request.body)
        book_title = data.get('title')
        book_author = data.get('author')
        book_genre = data.get('genre')
        if (not book_author) or (not book_title) or (not book_genre):
            return Response({'status': 'error', 'message': 'Request body must have 3 fields ["title", "author", "genre"]'}, status=400)
        if book_genre not in AVAILABLE_BOOK_GENRES:
            return Response({'status': 'error', 'message': 'Genre must be one of ' + str(AVAILABLE_BOOK_GENRES)}, status=400)
        with grpc.insecure_channel('books_service:50051') as channel:
            response = books_pb2_grpc.BooksServiceStub(channel).is_book_by_name(books_pb2.IsBookByNameRequest(book_name=book_title))
        if response.exists:
            return Response({'status': 'error', 'message': 'Book title exists'}, status=400)
        
        with grpc.insecure_channel('books_service:50051') as channel:
            books_pb2_grpc.BooksServiceStub(channel).add_book(books_pb2.Book(title=book_title, author=book_author, genre=book_genre, id=0))
        
        with grpc.insecure_channel('books_service:50051') as channel:
            response = books_pb2_grpc.BooksServiceStub(channel).get_book_by_name(books_pb2.GetBookByNameRequest(book_name=book_title))

        return Response({'status': 'success', 'title': response.title, 'author': response.author, 'genre': response.genre, 'id': response.id}, status=200)
    except json.JSONDecodeError:
        return Response({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return Response({'status': 'error', 'message': 'Internal server error'}, status=500)

@api_view(["POST"])
@login_required
def update_book(request):
    try:
        data = json.loads(request.body)
        user = request.user

        if not user.is_admin:
            return Response({'status': 'error', 'message': 'Unauthorized'}, status=401)


        curr_book = data.get('book')
        if not curr_book:
            return Response({'status': 'error', 'message': 'You must provicebook object'}, status=400)
        
        curr_title = curr_book.get('title')
        
        if not curr_title:
            return Response({'status': 'error', 'message': 'You must provide title in book object'}, status=400)

        new_title = data.get('title')
        new_author = data.get('author')
        new_genre = data.get('genre')

        if (not new_author) and (not new_genre) and (not new_title):
            return Response({'status': 'error', 'message': 'You must provice at least one of title, genre, author'}, status=400)

        with grpc.insecure_channel('books_service:50051') as channel:
            response = books_pb2_grpc.BooksServiceStub(channel).is_book_by_name(books_pb2.IsBookByNameRequest(book_name=curr_title))
        if not response.exists:
            return Response({'status': 'error', 'message': 'Book does not exist'}, status=400)

        with grpc.insecure_channel('books_service:50051') as channel:
            response = books_pb2_grpc.BooksServiceStub(channel).get_book_by_name(books_pb2.GetBookByNameRequest(book_name=curr_title))
        
        new_title = response.title if not new_title else new_title
        new_author = response.author if not new_author else new_author
        new_genre = response.genre if not new_genre else new_genre

        with grpc.insecure_channel('books_service:50051') as channel:
            books_pb2_grpc.BooksServiceStub(channel).update_book(books_pb2.UpdateBookRequest(book=books_pb2.Book(title=curr_title, author=response.author, genre=response.genre, id=1), title=new_title, author=new_author, genre=new_genre))
        
        with grpc.insecure_channel('books_service:50051') as channel:
            response = books_pb2_grpc.BooksServiceStub(channel).get_book_by_name(books_pb2.GetBookByNameRequest(book_name=new_title))

        return Response({'status': 'success', 'title': response.title, 'author': response.author, 'genre': response.genre, 'id': response.id}, status=200)
    except json.JSONDecodeError:
        return Response({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return Response({'status': 'error', 'message': 'Internal server error'}, status=500)

@api_view(["DELETE"])
@login_required
def delete_book(request):
    try:
        data = json.loads(request.body)
        user = request.user

        if not user.is_admin:
            return Response({'status': 'error', 'message': 'Unauthorized'}, status=401)
        
        title = data.get('title')
        
        if not title:
            return Response({'status': 'error', 'message': 'You must provide title'}, status=400)

        with grpc.insecure_channel('books_service:50051') as channel:
            response = books_pb2_grpc.BooksServiceStub(channel).is_book_by_name(books_pb2.IsBookByNameRequest(book_name=title))
        if not response.exists:
            return Response({'status': 'error', 'message': 'Book does not exist'}, status=400)

        with grpc.insecure_channel('books_service:50051') as channel:
            response = books_pb2_grpc.BooksServiceStub(channel).get_book_by_name(books_pb2.GetBookByNameRequest(book_name=title))
        
        author = response.author
        genre = response.genre

        with grpc.insecure_channel('books_service:50051') as channel:
            books_pb2_grpc.BooksServiceStub(channel).delete_book(books_pb2.Book(title=title, author=author, genre=genre, id=1))

        return Response({'status': 'success', 'message': 'Book successfully deleted'}, status=200)
    except json.JSONDecodeError:
        return Response({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return Response({'status': 'error', 'message': 'Internal server error'}, status=500)

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
@login_required
def borrow_book(request, book_pk):
    try:
        data = json.loads(request.body)
        user = request.user

        if not user.is_admin:
            return Response({'status': 'error', 'message': 'Unauthorized'}, status=401)
        
        title = data.get('title')
        
        if not title:
            return Response({'status': 'error', 'message': 'You must provide title'}, status=400)

        with grpc.insecure_channel('books_service:50051') as channel:
            response = books_pb2_grpc.BooksServiceStub(channel).is_book_by_name(books_pb2.IsBookByNameRequest(book_name=title))
        if not response.exists:
            return Response({'status': 'error', 'message': 'Book does not exist'}, status=400)

        with grpc.insecure_channel('books_service:50051') as channel:
            response = books_pb2_grpc.BooksServiceStub(channel).get_book_by_name(books_pb2.GetBookByNameRequest(book_name=title))
        
        author = response.author
        genre = response.genre

        with grpc.insecure_channel('books_service:50051') as channel:
            books_pb2_grpc.BooksServiceStub(channel).delete_book(books_pb2.Book(title=title, author=author, genre=genre, id=1))

        return Response({'status': 'success', 'message': 'Book successfully deleted'}, status=200)
    except json.JSONDecodeError:
        return Response({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return Response({'status': 'error', 'message': 'Internal server error'}, status=500)
    

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