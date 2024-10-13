from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class IsBookRequest(_message.Message):
    __slots__ = ("book_id",)
    BOOK_ID_FIELD_NUMBER: _ClassVar[int]
    book_id: int
    def __init__(self, book_id: _Optional[int] = ...) -> None: ...

class GetBookByIdRequest(_message.Message):
    __slots__ = ("book_id",)
    BOOK_ID_FIELD_NUMBER: _ClassVar[int]
    book_id: int
    def __init__(self, book_id: _Optional[int] = ...) -> None: ...

class IsBookResponse(_message.Message):
    __slots__ = ("exists",)
    EXISTS_FIELD_NUMBER: _ClassVar[int]
    exists: bool
    def __init__(self, exists: bool = ...) -> None: ...

class AllBooksResponse(_message.Message):
    __slots__ = ("books",)
    BOOKS_FIELD_NUMBER: _ClassVar[int]
    books: _containers.RepeatedCompositeFieldContainer[Book]
    def __init__(self, books: _Optional[_Iterable[_Union[Book, _Mapping]]] = ...) -> None: ...

class Book(_message.Message):
    __slots__ = ("title", "author", "genre")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    GENRE_FIELD_NUMBER: _ClassVar[int]
    title: str
    author: str
    genre: str
    def __init__(self, title: _Optional[str] = ..., author: _Optional[str] = ..., genre: _Optional[str] = ...) -> None: ...

class UpdateBookRequest(_message.Message):
    __slots__ = ("book", "title", "author", "genre")
    BOOK_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    GENRE_FIELD_NUMBER: _ClassVar[int]
    book: Book
    title: str
    author: str
    genre: str
    def __init__(self, book: _Optional[_Union[Book, _Mapping]] = ..., title: _Optional[str] = ..., author: _Optional[str] = ..., genre: _Optional[str] = ...) -> None: ...

class EmptyObject(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
