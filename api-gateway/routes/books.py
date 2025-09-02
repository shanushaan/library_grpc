from fastapi import APIRouter
from pydantic import BaseModel, Field, validator
from services.book_service import BookService
from core.grpc_client import get_grpc_client
from core.validation import validate_positive_integer

router = APIRouter()

class BookSearchRequest(BaseModel):
    query: str = Field(default="", max_length=200)
    
    @validator('query')
    def validate_query(cls, v):
        return v.strip() if v else ""

class IssueBookRequest(BaseModel):
    book_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)
    
    @validator('book_id')
    def validate_book_id(cls, v):
        return validate_positive_integer(v, "Book ID")
    
    @validator('user_id')
    def validate_user_id(cls, v):
        return validate_positive_integer(v, "User ID")

class ReturnBookRequest(BaseModel):
    transaction_id: int = Field(..., gt=0)
    
    @validator('transaction_id')
    def validate_transaction_id(cls, v):
        return validate_positive_integer(v, "Transaction ID")

@router.get('/user/books/search')
async def search_books(q: str = ""):
    client = await get_grpc_client()
    book_service = BookService(client)
    return await book_service.search_books(q)

@router.get('/admin/books')
async def list_books_admin(q: str = ""):
    return await search_books(q)

@router.post('/admin/issue-book')
async def issue_book(request: IssueBookRequest):
    client = await get_grpc_client()
    book_service = BookService(client)
    return await book_service.issue_book(request.book_id, request.user_id)

@router.post('/admin/return-book')
async def return_book(request: ReturnBookRequest):
    client = await get_grpc_client()
    book_service = BookService(client)
    return await book_service.return_book(request.transaction_id)