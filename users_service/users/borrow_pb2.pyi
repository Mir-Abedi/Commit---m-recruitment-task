from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class IsBorrowedRequest(_message.Message):
    __slots__ = ("book_id",)
    BOOK_ID_FIELD_NUMBER: _ClassVar[int]
    book_id: int
    def __init__(self, book_id: _Optional[int] = ...) -> None: ...

class IsBorrowedByRequest(_message.Message):
    __slots__ = ("book_id", "user_id")
    BOOK_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    book_id: int
    user_id: int
    def __init__(self, book_id: _Optional[int] = ..., user_id: _Optional[int] = ...) -> None: ...

class IsBorrowedResponse(_message.Message):
    __slots__ = ("is_borrowed",)
    IS_BORROWED_FIELD_NUMBER: _ClassVar[int]
    is_borrowed: bool
    def __init__(self, is_borrowed: bool = ...) -> None: ...

class BorrowRequest(_message.Message):
    __slots__ = ("user_id", "book_id")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    BOOK_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    book_id: int
    def __init__(self, user_id: _Optional[int] = ..., book_id: _Optional[int] = ...) -> None: ...

class ReturnRequest(_message.Message):
    __slots__ = ("book_id", "user_id")
    BOOK_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    book_id: int
    user_id: int
    def __init__(self, book_id: _Optional[int] = ..., user_id: _Optional[int] = ...) -> None: ...

class EmptyObject(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
