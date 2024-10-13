from concurrent import futures
import grpc
import books_pb2
import books_pb2_grpc
from books.models import Book

class Books(books_pb2_grpc.BooksServiceServicer):
    def is_book(self, request, context):
        return books_pb2.IsBookResponse(Book.objects.filter(id=request.book_id).exists())

    def get_book_by_id(self, request, context):
        book = Book.objects.get(id=request.book_id)
        return books_pb2.Book(book.title, book.author, book.genre)

    def all_books(self, request, context):
        return books_pb2.AllBooksResponse(books=[Book(i.title, i.author, i.genre) for i in Book.objects.all()])

    def add_book(self, request, context):
        book = Book(title=request.title, author=request.title, genre=request.genre)
        book.save()
        return books_pb2.EmptyObject()

    def update_book(self, request, context):
        book = Book.objects.get(title=request.book.title)
        if not book:
            return books_pb2.EmptyObject()
        book.title = request.title
        book.author = request.author
        book.genre = request.genre
        book.save()
        return books_pb2.EmptyObject()

    def delete_book(self, request, context):
        book = Book.objects.get(title=request.book.title)
        if not book:
            return books_pb2.EmptyObject()
        book.delete()
        return books_pb2.EmptyObject()
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    books_pb2_grpc.add_BooksServiceServicer_to_server(Books(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__=="__main__":
    serve()