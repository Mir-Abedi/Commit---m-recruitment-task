from concurrent import futures
import grpc
from concurrent import futures
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import borrow_pb2
import borrow_pb2_grpc


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


class BorrowRecord(Base):
    __tablename__ = 'BORROWTABLE'

    book_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)

    def __repr__(self) -> str:
        return f"{self.id}"

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

class BorrowService(borrow_pb2_grpc.BorrowServiceServicer):
    def is_borrowed(self, request, context):
        res = session.query(session.query(BorrowRecord).filter(BorrowRecord.book_id == request.book_id).exists()).scalar()
        return borrow_pb2.IsBorrowedResponse(is_borrowed=res)

    def is_borrowed_by(self, request, context):
        res = session.query(session.query(BorrowRecord).filter(BorrowRecord.book_id == request.book_id).filter(BorrowRecord.user_id == request.user_id).exists()).scalar()
        return borrow_pb2.IsBorrowedResponse(is_borrowed=res)

    def borrow(self, request, context):
        br = BorrowRecord(book_id=request.book_id, user_id=request.user_id)
        session.add(br)
        session.commit()
        return borrow_pb2.EmptyObject()


    def return_book(self, request, context):
        res = session.query(BorrowRecord).filter(BorrowRecord.book_id == request.book_id).filter(BorrowRecord.user_id == request.user_id).first()
        if not res:
            return borrow_pb2.EmptyObject()
        session.delete(res)
        session.commit()
        return borrow_pb2.EmptyObject()
        
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    borrow_pb2_grpc.add_BorrowServiceServicer_to_server(BorrowService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__=="__main__":
    serve()