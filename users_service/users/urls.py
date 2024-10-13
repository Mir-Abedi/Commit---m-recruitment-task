from django.urls import path
from . import views

urlpatterns = [
    path('books/all/', views.all_books, name='all books'),
    path('books/add/', views.add_book, name='add book'),
    path('books/update/', views.update_book, name='all_books'),
    path('books/delete/', views.delete_book, name="delete book"),
    path('users/register/', views.register_user, name='register user'),
    path('users/login/', views.login_user, name='login user'),
    path('borrow/<int:book_pk>', views.borrow_book, name='borrow book'),
    path('return/<int:book_pk>', views.all_books, name='return book'),
    path('users/update/', views.update_user, name='update user'),  
    path('users/logout/', views.logout_user, name="user logout"),
    path('users/me/', views.me, name="user profile"),
]