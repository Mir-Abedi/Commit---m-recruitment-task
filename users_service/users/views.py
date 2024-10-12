from rest_framework.decorators import api_view
from rest_framework.response import Response

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
    pass

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