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
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

AVAILABLE_BOOK_GENRES = ["Fantasy", "Romance", "Horror", "Sci-Fi", "Thriller"]

@swagger_auto_schema(
    operation_id='all_books',
    method='GET',
    operation_description="An endpoint to retrieve all the books",
    operation_summary="List of all books",
    responses={
        200: openapi.Response('[Books]'),
    }
)
@api_view(["GET"])
def all_books(request):
    try:
        with grpc.insecure_channel('books_service:50051') as channel:
            response = books_pb2_grpc.BooksServiceStub(channel).all_books(books_pb2.EmptyObject())
        return Response([{'title': i.title, 'author': i.author, 'genre': i.genre, 'id': i.id} for i in response.books], status=200)
    except Exception as e:
        return Response({'status': 'error', 'message': 'Internal server error'}, status=500)
        
@swagger_auto_schema(
    operation_id='add_book',
    method='POST',
    request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the book'),
                'author': openapi.Schema(type=openapi.TYPE_STRING, description='Author of the book'),
                'genre': openapi.Schema(type=openapi.TYPE_STRING, description='Genre of the book. must be one of ' + str(AVAILABLE_BOOK_GENRES))
            },
            required=['title', 'author', 'genre']
        ),
    operation_description="An endpoint that adds a book to the library.",
    operation_summary="Create a book",
    responses={
        200: openapi.Response('Book found'),
        400: 'Less than 3 fields given'
    }
)
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

@swagger_auto_schema(
    operation_id='update_book',
    method='POST',
    request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the book'),
                'author': openapi.Schema(type=openapi.TYPE_STRING, description='Author of the book'),
                'genre': openapi.Schema(type=openapi.TYPE_STRING, description='Genre of the book. must be one of ' + str(AVAILABLE_BOOK_GENRES)),
                'book': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description='Book to be replaced',
                    properties={
                        'title': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the book'),
                        'author': openapi.Schema(type=openapi.TYPE_STRING, description='Author of the book'),
                        'genre': openapi.Schema(type=openapi.TYPE_STRING, description='Genre of the book'),
                    },
                    required=['title']
                )
            },
            required=[]
        ),
    operation_description="An endpoint that updated a book in the library. at least one of title, author, genre should be provided. You must have admin priviliges.",
    operation_summary="Update a book",
    responses={
        200: openapi.Response('Book updated'),
        400: 'book title not given'
    }
)
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

@swagger_auto_schema(
    operation_id='delete_book',
    method='DELETE',
    request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the book'),
            },
            required=['title']
        ),
    operation_description="An endpoint that deletes a book. You must have admin priviliges.",
    operation_summary="Delete a book",
    responses={
        200: openapi.Response('Book deleted'),
        400: 'book title not given'
    }
)
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
        user = request.user

        with grpc.insecure_channel('books_service:50051') as channel:
            response = books_pb2_grpc.BooksServiceStub(channel).is_book(books_pb2.IsBookRequest(book_id=book_pk))
        if not response.exists:
            return Response({'status': 'error', 'message': 'Book does not exist'}, status=400)
        
        with grpc.insecure_channel('borrow_service:50052') as channel:
            response = borrow_pb2_grpc.BorrowServiceStub(channel).is_borrowed(borrow_pb2.IsBorrowedRequest(book_id=book_pk))
        if response.is_borrowed:
            return Response({'status': 'error', 'message': 'Book is already borrowed'}, status=400)

        with grpc.insecure_channel('borrow_service:50052') as channel:
            response = borrow_pb2_grpc.BorrowServiceStub(channel).borrow(borrow_pb2.BorrowRequest(user_id=user.id, book_id=book_pk))
        
        return Response({'status': 'success', 'message': 'Book successfully borrowed'}, status=200)
    except Exception as e:
        return Response({'status': 'error', 'message': 'Internal server error'}, status=500)
    

@api_view(["POST"])
@login_required
def return_book(request, book_pk):
    try:
        user = request.user

        with grpc.insecure_channel('books_service:50051') as channel:
            response = books_pb2_grpc.BooksServiceStub(channel).is_book(books_pb2.IsBookRequest(book_id=book_pk))
        if not response.exists:
            return Response({'status': 'error', 'message': 'Book does not exist'}, status=400)
        
        with grpc.insecure_channel('borrow_service:50052') as channel:
            response = borrow_pb2_grpc.BorrowServiceStub(channel).is_borrowed_by(borrow_pb2.IsBorrowedByRequest(book_id=book_pk, user_id=user.id))
        if not response.is_borrowed:
            return Response({'status': 'error', 'message': 'Book is not borrowed by this user'}, status=400)

        with grpc.insecure_channel('borrow_service:50052') as channel:
            response = borrow_pb2_grpc.BorrowServiceStub(channel).return_book(borrow_pb2.ReturnRequest(user_id=user.id, book_id=book_pk))
        
        return Response({'status': 'success', 'message': 'Book successfully returned'}, status=200)
    except Exception as e:
        return Response({'status': 'error', 'message': 'Internal server error'}, status=500)

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