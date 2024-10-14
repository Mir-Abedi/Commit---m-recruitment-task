from django.urls import path
from . import views

urlpatterns = [
    path('books/all/', views.all_books, name='all books'),
    path('books/add/', views.add_book, name='add book'),
    path('books/update/', views.update_book, name='all_books'),
    path('books/delete/', views.delete_book, name="delete book"),
    path('books/search/', views.search_books, name="search books"),
    path('users/register/', views.register_user, name='register user'),
    path('users/login/', views.login_user, name='login user'),
    path('books/borrow/<int:book_pk>', views.borrow_book, name='borrow book'),
    path('books/return/<int:book_pk>', views.return_book, name='return book'),
    path('books/is_available/<int:book_pk>', views.is_available_in_path, name='is book available'),
    path('books/is_available/', views.is_available, name='is book available'),
    path('users/update/', views.update_user, name='update user'),  
    path('users/logout/', views.logout_user, name="user logout"),
    path('users/me/', views.me, name="user profile"),
]