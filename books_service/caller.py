from concurrent import futures
import grpc
from concurrent import futures
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import books_pb2
import books_pb2_grpc


db_config = {
    'dbname': 'gres2',
    'user': 'gres',
    'password': 'gres',
    'host': '127.0.0.1',
    'port': '5433',
}

DATABASE_URL = "postgresql://gres:gres@db:5432/gres"
engine = create_engine(DATABASE_URL, echo=True)


class Base(DeclarativeBase):
    pass


class Book(Base):
    __tablename__ = 'BOOKSTABLE'

    id = Column(Integer, primary_key=True)
    author = Column(String)
    title = Column(String)
    genre = Column(String)

    def __repr__(self) -> str:
        return f"{self.id}"

# Base.metadata.create_all(engine)

# Session = sessionmaker(bind=engine)
# session = Session()

class Books(books_pb2_grpc.BooksServiceServicer):
    def is_book(self, request, context):
        res = session.query(session.query(Book).filter(Book.id == request.book_id).exists()).scalar()
        return books_pb2.IsBookResponse(res)

    def get_book_by_id(self, request, context):
        book = session.query(Book).filter(Book.id == request.book_id).first()
        return books_pb2.Book(book.title, book.author, book.genre)

    def all_books(self, request, context):
        return books_pb2.AllBooksResponse([Book(title="A", author="B", genre="C")])
        arr = session.query(Book).all()
        return books_pb2.AllBooksResponse(books=[Book(i.title, i.author, i.genre) for i in arr])

    def add_book(self, request, context):
        book = Book(title=request.title, author=request.title, genre=request.genre)
        session.add(book)
        session.commit()
        return books_pb2.EmptyObject()

    def update_book(self, request, context):
        book = session.query(Book).filter(Book.title == request.book.title).first()
        if not book:
            return books_pb2.EmptyObject()
        book.title = request.title
        book.author = request.author
        book.genre = request.genre
        session.commit()
        return books_pb2.EmptyObject()

    def delete_book(self, request, context):
        book = session.query(Book).filter(Book.title == request.book.title).first()
        if not book:
            return books_pb2.EmptyObject()
        session.delete(book)
        session.commit()
        return books_pb2.EmptyObject()
    
# def serve():
#     b1 = Book(title="Amir", author="Amir2", genre="aaaa")
#     session.add(b1)
#     session.commit()
#     server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
#     books_pb2_grpc.add_BooksServiceServicer_to_server(Books(), server)
#     server.add_insecure_port('[::]:50051')
#     server.start()
#     server.wait_for_termination()

# if __name__=="__main__":
#     serve()

with grpc.insecure_channel('localhost:50051') as channel:
    response = books_pb2_grpc.BooksServiceStub(channel).all_books(books_pb2.EmptyObject())
    for i in response.books:
        print(type(i.title))
    print([{i:i} for i in range(10)])
