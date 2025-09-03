from connection_pool import db_pool
import library_service_pb2_grpc
from services.auth_service import AuthService
from services.book_service import BookService
from services.transaction_service import TransactionService
from services.request_service import RequestService
from services.user_service import UserService

class LibraryServiceImpl(library_service_pb2_grpc.LibraryServiceServicer):
    
    def __init__(self):
        # Initialize connection pool
        db_pool.initialize_pool()
        # Initialize domain services
        self.auth_service = AuthService()
        self.book_service = BookService()
        self.transaction_service = TransactionService()
        self.request_service = RequestService()
        self.user_service = UserService()
    
    # Authentication
    def AuthenticateUser(self, request, context):
        return self.auth_service.authenticate_user(request, context)
    
    # Books
    def GetBooks(self, request, context):
        return self.book_service.get_books(request, context)
    
    def CreateBook(self, request, context):
        return self.book_service.create_book(request, context)
    
    def UpdateBook(self, request, context):
        return self.book_service.update_book(request, context)
    
    def DeleteBook(self, request, context):
        return self.book_service.delete_book(request, context)
    
    # Users
    def GetUsers(self, request, context):
        return self.user_service.get_users(request, context)
    
    def CreateUser(self, request, context):
        return self.user_service.create_user(request, context)
    
    def UpdateUser(self, request, context):
        return self.user_service.update_user(request, context)
    
    def GetUserStats(self, request, context):
        return self.user_service.get_user_stats(request, context)
    
    def GetUserTransactions(self, request, context):
        return self.user_service.get_user_transactions(request, context)
    
    # Transactions
    def GetTransactions(self, request, context):
        return self.transaction_service.get_transactions(request, context)
    
    def IssueBook(self, request, context):
        return self.transaction_service.issue_book(request, context)
    
    def ReturnBook(self, request, context):
        return self.transaction_service.return_book(request, context)
    
    # Requests
    def CreateUserBookRequest(self, request, context):
        return self.request_service.create_book_request(request, context)
    
    def GetBookRequests(self, request, context):
        return self.request_service.get_book_requests(request, context)
    
    def ApproveBookRequest(self, request, context):
        return self.request_service.approve_book_request(request, context)
    
    def RejectBookRequest(self, request, context):
        return self.request_service.reject_book_request(request, context)