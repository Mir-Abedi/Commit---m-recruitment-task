from concurrent import futures
import grpc
from concurrent import futures
from sqlalchemy import create_engine, Column, Integer, DateTime, func
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import borrow_pb2
import borrow_pb2_grpc
from datetime import datetime, timedelta
import os

class Base(DeclarativeBase):
    pass

class BorrowRecord(Base):
    __tablename__ = 'BORROWTABLE'

    book_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self) -> str:
        return f"{self.id}"

DATABASE_URL = f'postgresql://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@{os.getenv("POSTGRES_HOST")}:{os.getenv("POSTGRES_PORT")}/{os.getenv("POSTGRES_DB")}'
engine = create_engine(DATABASE_URL, echo=True)
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
            return borrow_pb2.ReturnResonse(penalty=0)
        session.delete(res)
        session.commit()
        return borrow_pb2.ReturnResonse(penalty=self.penalty_function(res.created_at))
    
    def delete_book(self, request, context):
        res = session.query(BorrowRecord).filter(BorrowRecord.book_id == request.book_id).first()
        if not res:
            return borrow_pb2.EmptyObject()
        session.delete(res)
        session.commit()
        return borrow_pb2.EmptyObject()
        
    def penalty_function(self, record_time):
        if record_time > datetime.now() - timedelta(days=60):
            return 50
        elif record_time > datetime.now() - timedelta(days=30):
            return 20
        elif record_time > datetime.now() - timedelta(days=7):
            return 5
        else:
            return 0

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    borrow_pb2_grpc.add_BorrowServiceServicer_to_server(BorrowService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()

if __name__=="__main__":
    serve()