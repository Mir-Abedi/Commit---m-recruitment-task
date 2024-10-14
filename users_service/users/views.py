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
    method='PUT',
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
@api_view(["PUT"])
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

        with grpc.insecure_channel('borrow_service:50052') as channel:
            borrow_pb2_grpc.BorrowServiceStub(channel).delete_book(borrow_pb2.DeleteRequest(book_id=response.id))

        with grpc.insecure_channel('books_service:50051') as channel:
            books_pb2_grpc.BooksServiceStub(channel).delete_book(books_pb2.Book(title=title, author=author, genre=genre, id=1))

        return Response({'status': 'success', 'message': 'Book successfully deleted'}, status=200)
    except json.JSONDecodeError:
        return Response({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return Response({'status': 'error', 'message': 'Internal server error'}, status=500)

@swagger_auto_schema(
    operation_id='register_user',
    method='POST',
    request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='User full name'),
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Your email'),
                'phone_num': openapi.Schema(type=openapi.TYPE_STRING, description='Your phone number'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='User\'s passowrd'),
                'is_admin': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='If the user should be created as admin. defaults to False'),
                
            },
            required=['name', 'username', 'email', 'phone_num', 'password']
        ),
    operation_description="An endpoint registers a user.",
    operation_summary="Register user",
    responses={
        200: openapi.Response('User registered'),
        400: 'Credentials not provided'
    }
)
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

@swagger_auto_schema(
    operation_id='login_user',
    method='POST',
    request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='User\'s passowrd'),                
            },
            required=['username', 'password']
        ),
    operation_description="An endpoint that is used for logging in. Some endpoints logged in users.",
    operation_summary="Login user",
    responses={
        200: openapi.Response('User logged in'),
        400: 'Invalid credentials'
    }
)
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

@swagger_auto_schema(
    operation_id='logout_user',
    method='POST',
    operation_description="An endpoint that is used for logging out. Login required.",
    operation_summary="Logout user",
    responses={
        200: openapi.Response('User logged out'),
    }
)
@api_view(["POST"])
@login_required
def logout_user(request):
    logout(request)
    return Response({'status': 'success', 'message': 'Logged out successfully'}, status=200)

@swagger_auto_schema(
    operation_id='borrow_book',
    method='POST',
    manual_parameters=[
            openapi.Parameter(
                'book_pk',
                openapi.IN_PATH,
                description="Primary key of the book",
                type=openapi.TYPE_INTEGER
            )
        ],
    operation_description="An endpoint that is used for borrowing books. Requires log in.",
    operation_summary="Borrow book",
    responses={
        200: openapi.Response('Book borrowed'),
        400: 'Book not available'
    }
)
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
    
@swagger_auto_schema(
    operation_id='return_book',
    method='POST',
    manual_parameters=[
            openapi.Parameter(
                'book_pk',
                openapi.IN_PATH,
                description="Primary key of the book",
                type=openapi.TYPE_INTEGER
            )
        ],
    operation_description="An endpoint that is used for returning books. Requires log in.",
    operation_summary="Return book",
    responses={
        200: openapi.Response('Book returned'),
        400: 'Book not borrowed'
    }
)
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
        
        user.balance -= response.penalty
        return Response({'status': 'success', 'message': 'Book successfully returned, return penalty: ' + str(response.penalty) + '$'}, status=200)
    except Exception as e:
        return Response({'status': 'error', 'message': 'Internal server error'}, status=500)

@swagger_auto_schema(
    operation_id='update_user',
    method='PUT',
    request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='User full name'),
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Your email'),
                'phone_num': openapi.Schema(type=openapi.TYPE_STRING, description='Your phone number'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='User\'s passowrd'),
                'is_admin': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='If the user should be created as admin. defaults to False'),
                
            },
            required=[]
        ),
    operation_description="An endpoint to change user profile. requires log in.",
    operation_summary="update user",
    responses={
        200: openapi.Response('User updated'),
        400: 'Bad json data'
    }
)
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
        is_admin = data.get('is_admin', False)

        if (not name) and (not username) and (not email) and (not password) and (not phone_num):
            return Response({'status': 'error', 'message': 'Provide at least one field'}, status=400)

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
        
        user.name = user.name if not name else name
        user.username = user.username if not username else username
        user.email = user.email if not email else email
        user.phone_num = user.phone_num if not phone_num else phone_num
        user.is_admin = user.is_admin if user.is_admin else is_admin
        user.password = user.password if not password else make_password(password)

        user.save()
        return Response({'status': 'success', 'message': 'Profile updated'}, status=200)

    except Exception as e:
        print(e)
        return Response({'status': 'error', 'message': 'Internal server error'}, status=500)

@swagger_auto_schema(
    operation_id='me_user',
    method='GET',
    operation_description="An endpoint that is used for retrieving self data. requires log in.",
    operation_summary="User profile",
    responses={
        200: openapi.Response('{user_data}'),
    }
)
@api_view(["GET"])
@login_required
def me(request):
    try: 
        user = request.user
        return Response({'status': 'success', 'user_id': user.id, 'name': user.name, 'username': user.username, 
                         'email': user.email, 'phone_num': user.phone_num, 'is_admin': user.is_admin, 'balance': user.balance}, status=200)

    except Exception as e:
        print(e)
        return Response({'status': 'error', 'message': 'Internal server error'}, status=500)
    
@swagger_auto_schema(
    operation_id='search_books',
    method='GET',
    request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Title to search for'),
                'author': openapi.Schema(type=openapi.TYPE_STRING, description='Author to search for'), 
                'genre': openapi.Schema(type=openapi.TYPE_STRING, description='Genre to search for'), 
            },
            required=[]
        ),
    operation_description="An endpoint to retrieve all the books based on certain criteria",
    operation_summary="Search books",
    responses={
        200: openapi.Response('[Books]'),
        400: 'No field provided'
    }
)
@api_view(["GET"])
def search_books(request):
    try:
        data = json.loads(request.body)
        title = data.get('title')
        author = data.get('author')
        genre = data.get('genre')

        if (not title) and (not author) and (not genre):
            return Response({'status': 'error', 'message': 'Provide at least one field'}, status=400) 
        
        criteria = []
        if title:
            criteria.append(lambda x: x.title.startswith(title))

        if author:
            criteria.append(lambda x: x.author.startswith(author))
        
        if genre:
            criteria.append(lambda x: x.genre.startswith(genre))

        with grpc.insecure_channel('books_service:50051') as channel:
            response = books_pb2_grpc.BooksServiceStub(channel).all_books(books_pb2.EmptyObject())
        

        return Response([{'title': i.title, 'author': i.author, 'genre': i.genre, 'id': i.id} for i in search_based_on_func(response.books, criteria)], status=200)
    except Exception as e:
        return Response({'status': 'error', 'message': 'Internal server error'}, status=500)

def search_based_on_func(arr, fs):
    return [i for i in arr if all([f(i) for f in fs])]