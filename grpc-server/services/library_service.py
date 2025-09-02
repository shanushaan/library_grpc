import grpc
import hashlib
from datetime import datetime, timedelta
import sys
import os
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from shared.models import User, Book, Transaction, BookRequest
from shared.database import SessionLocal
import library_service_pb2
import library_service_pb2_grpc

# Configure structured JSON logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record),
            "service": "grpc-server",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.name
        }
        # Add extra fields if present
        if hasattr(record, '__dict__'):
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename', 'module', 'lineno', 'funcName', 'created', 'msecs', 'relativeCreated', 'thread', 'threadName', 'processName', 'process', 'getMessage', 'exc_info', 'exc_text', 'stack_info']:
                    log_entry[key] = value
        return json.dumps(log_entry)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.handlers = [handler]
logger.propagate = False

class LibraryServiceImpl(library_service_pb2_grpc.LibraryServiceServicer):
    
    def AuthenticateUser(self, request, context):
        logger.info("Authentication attempt", extra={"username": request.username, "method": "AuthenticateUser"})
        db = SessionLocal()
        try:
            password_hash = hashlib.sha256(request.password.encode()).hexdigest()
            user = db.query(User).filter(
                User.username == request.username,
                User.password_hash == password_hash,
                User.is_active.is_(True)
            ).first()
            
            if user:
                user.last_login = datetime.utcnow()
                db.commit()
                logger.info("Authentication successful", extra={"username": request.username, "role": user.role, "user_id": user.user_id})
                
                return library_service_pb2.AuthResponse(
                    success=True,
                    user=library_service_pb2.User(
                        user_id=user.user_id,
                        username=user.username,
                        email=user.email,
                        role=user.role,
                        is_active=user.is_active
                    ),
                    message="Authentication successful"
                )
            else:
                logger.warning("Authentication failed", extra={"username": request.username, "reason": "invalid_credentials"})
                return library_service_pb2.AuthResponse(
                    success=False,
                    message="Invalid credentials"
                )
        except Exception as e:
            logger.error("Error during authentication", extra={"username": request.username, "error": str(e), "error_type": "database_error"})
            raise
        finally:
            db.close()
    
    def GetBooks(self, request, context):
        db = SessionLocal()
        try:
            query = db.query(Book).filter(Book.is_deleted.is_(False))
            if request.search_query:
                query = query.filter(
                    (Book.title.ilike(f"%{request.search_query}%")) |
                    (Book.author.ilike(f"%{request.search_query}%")) |
                    (Book.genre.ilike(f"%{request.search_query}%"))
                )
            
            books = query.all()
            book_list = []
            
            for book in books:
                book_list.append(library_service_pb2.Book(
                    book_id=book.book_id,
                    title=book.title,
                    author=book.author or "",
                    genre=book.genre or "",
                    published_year=book.published_year or 0,
                    available_copies=book.available_copies,
                    is_deleted=book.is_deleted or False
                ))
            
            return library_service_pb2.GetBooksResponse(books=book_list)
        finally:
            db.close()
    
    def GetUsers(self, request, context):
        db = SessionLocal()
        try:
            users = db.query(User).all()
            user_list = []
            
            for user in users:
                user_list.append(library_service_pb2.User(
                    user_id=user.user_id,
                    username=user.username,
                    email=user.email,
                    role=user.role,
                    is_active=user.is_active
                ))
            
            return library_service_pb2.GetUsersResponse(users=user_list)
        finally:
            db.close()
    
    def GetTransactions(self, request, context):
        db = SessionLocal()
        try:
            query = db.query(Transaction)
            if request.user_id:
                query = query.filter(Transaction.user_id == request.user_id)
            if request.status:
                query = query.filter(Transaction.status == request.status)
            
            transactions = query.order_by(Transaction.transaction_date.desc()).all()
            transaction_list = []
            
            for txn in transactions:
                transaction_list.append(library_service_pb2.Transaction(
                    transaction_id=txn.transaction_id,
                    member_id=txn.user_id,
                    book_id=txn.book_id,
                    transaction_type=txn.transaction_type,
                    transaction_date=txn.transaction_date.isoformat() if txn.transaction_date else "",
                    due_date=txn.due_date.isoformat() if txn.due_date else "",
                    return_date=txn.return_date.isoformat() if txn.return_date else "",
                    status=txn.status,
                    fine_amount=txn.fine_amount or 0
                ))
            
            return library_service_pb2.GetTransactionsResponse(transactions=transaction_list)
        finally:
            db.close()
    
    def IssueBook(self, request, context):
        db = SessionLocal()
        try:
            # Validate book availability
            book = db.query(Book).filter(Book.book_id == request.book_id).first()
            if not book or book.available_copies <= 0:
                return library_service_pb2.TransactionResponse(
                    success=False,
                    message="Book not available"
                )
            
            # Validate user exists
            user = db.query(User).filter(User.user_id == request.member_id).first()
            if not user:
                return library_service_pb2.TransactionResponse(
                    success=False,
                    message="User not found"
                )
            
            # Check if user already has this book borrowed
            existing_borrow = db.query(Transaction).filter(
                Transaction.user_id == request.member_id,
                Transaction.book_id == request.book_id,
                Transaction.status == 'BORROWED'
            ).first()
            if existing_borrow:
                return library_service_pb2.TransactionResponse(
                    success=False,
                    message="User already has this book borrowed. Cannot borrow same book multiple times."
                )
            
            # Check if user already has 3 books borrowed
            if user.role == 'user':
                borrowed_count = db.query(Transaction).filter(
                    Transaction.user_id == request.member_id,
                    Transaction.status == 'BORROWED'
                ).count()
                if borrowed_count >= 3:
                    return library_service_pb2.TransactionResponse(
                        success=False,
                        message="User already has 3 books borrowed. Please return a book first."
                    )
            
            # Create transaction
            transaction = Transaction(
                user_id=request.member_id,  # Using user_id instead of member_id
                book_id=request.book_id,
                transaction_type='BORROW',
                transaction_date=datetime.utcnow(),
                due_date=datetime.utcnow() + timedelta(days=30),
                status='BORROWED',
                fine_amount=0
            )
            
            # Update book availability
            book.available_copies -= 1
            
            db.add(transaction)
            db.commit()
            
            return library_service_pb2.TransactionResponse(
                success=True,
                transaction=library_service_pb2.Transaction(
                    transaction_id=transaction.transaction_id,
                    member_id=transaction.user_id,
                    book_id=transaction.book_id,
                    transaction_type=transaction.transaction_type,
                    status=transaction.status
                ),
                message="Book issued successfully"
            )
        except Exception as e:
            db.rollback()
            return library_service_pb2.TransactionResponse(
                success=False,
                message=str(e)
            )
        finally:
            db.close()
    
    def ReturnBook(self, request, context):
        db = SessionLocal()
        try:
            transaction = db.query(Transaction).filter(
                Transaction.transaction_id == request.transaction_id,
                Transaction.status == 'BORROWED'
            ).first()
            
            if not transaction:
                return library_service_pb2.TransactionResponse(
                    success=False,
                    message="Transaction not found or book already returned"
                )
            
            # Update transaction
            return_date = datetime.utcnow()
            transaction.return_date = return_date
            transaction.status = 'RETURNED'
            
            # Calculate fine if overdue
            if transaction.due_date and return_date > transaction.due_date:
                days_overdue = (return_date - transaction.due_date).days
                transaction.fine_amount = days_overdue * 10
            
            # Update book availability
            book = db.query(Book).filter(Book.book_id == transaction.book_id).first()
            if book:
                book.available_copies += 1
            
            db.commit()
            
            return library_service_pb2.TransactionResponse(
                success=True,
                transaction=library_service_pb2.Transaction(
                    transaction_id=transaction.transaction_id,
                    member_id=transaction.member_id,
                    book_id=transaction.book_id,
                    transaction_type=transaction.transaction_type,
                    status=transaction.status,
                    fine_amount=transaction.fine_amount
                ),
                message="Book returned successfully"
            )
        except Exception as e:
            db.rollback()
            return library_service_pb2.TransactionResponse(
                success=False,
                message=str(e)
            )
        finally:
            db.close()
    
    def CreateUserBookRequest(self, request, context):
        logger.info("Creating book request", extra={"user_id": request.user_id, "book_id": request.book_id, "request_type": request.request_type, "method": "CreateUserBookRequest"})
        db = SessionLocal()
        try:
            book_request = BookRequest(
                user_id=request.user_id,
                book_id=request.book_id,
                request_type=request.request_type,
                status='PENDING',
                notes=request.notes,
                transaction_id=request.transaction_id if request.transaction_id else None
            )
            
            db.add(book_request)
            db.commit()
            logger.info("Book request created successfully", extra={"request_id": book_request.request_id, "user_id": request.user_id, "book_id": request.book_id})
            
            return library_service_pb2.BookRequestResponse(
                success=True,
                request=library_service_pb2.BookRequest(
                    request_id=book_request.request_id,
                    user_id=book_request.user_id,
                    book_id=book_request.book_id,
                    request_type=book_request.request_type,
                    status=book_request.status
                ),
                message="Request created successfully"
            )
        except Exception as e:
            logger.error("Error creating book request", extra={"user_id": request.user_id, "book_id": request.book_id, "error": str(e), "error_type": "database_error"})
            db.rollback()
            return library_service_pb2.BookRequestResponse(
                success=False,
                message=str(e)
            )
        finally:
            db.close()
    
    def GetBookRequests(self, request, context):
        db = SessionLocal()
        try:
            query = db.query(BookRequest)
            if request.status:
                query = query.filter(BookRequest.status == request.status)
            
            requests = query.order_by(BookRequest.request_date.desc()).all()
            request_list = []
            
            for req in requests:
                request_list.append(library_service_pb2.BookRequest(
                    request_id=req.request_id,
                    user_id=req.user_id,
                    book_id=req.book_id,
                    request_type=req.request_type,
                    status=req.status,
                    request_date=req.request_date.isoformat() if req.request_date else "",
                    notes=req.notes or "",
                    transaction_id=getattr(req, 'transaction_id', 0) or 0
                ))
            
            return library_service_pb2.GetBookRequestsResponse(requests=request_list)
        finally:
            db.close()
    
    def ApproveBookRequest(self, request, context):
        logger.info(f"Approving book request: request_id={request.request_id}")
        db = SessionLocal()
        try:
            book_request = db.query(BookRequest).filter(
                BookRequest.request_id == request.request_id,
                BookRequest.status == 'PENDING'
            ).first()
            
            if not book_request:
                logger.warning(f"Book request not found or already processed: request_id={request.request_id}")
                return library_service_pb2.BookRequestResponse(
                    success=False,
                    message="Request not found or already processed"
                )
            
            # Process based on request type
            if book_request.request_type == 'ISSUE':
                # Issue book logic (similar to IssueBook)
                book = db.query(Book).filter(Book.book_id == book_request.book_id).first()
                if not book or book.available_copies <= 0:
                    return library_service_pb2.BookRequestResponse(
                        success=False,
                        message="Book no longer available"
                    )
                
                # Check if user already has 3 books borrowed
                user = db.query(User).filter(User.user_id == book_request.user_id).first()
                if user and user.role == 'user':
                    borrowed_count = db.query(Transaction).filter(
                        Transaction.user_id == book_request.user_id,
                        Transaction.status == 'BORROWED'
                    ).count()
                    if borrowed_count >= 3:
                        return library_service_pb2.BookRequestResponse(
                            success=False,
                            message="User already has 3 books borrowed. Please return a book first."
                        )
                
                transaction = Transaction(
                    user_id=book_request.user_id,  # Using user_id instead of member_id
                    book_id=book_request.book_id,
                    transaction_type='BORROW',
                    transaction_date=datetime.utcnow(),
                    due_date=datetime.utcnow() + timedelta(days=30),
                    status='BORROWED',
                    fine_amount=0
                )
                
                book.available_copies -= 1
                db.add(transaction)
            elif book_request.request_type == 'RETURN':
                # Return book logic
                if book_request.transaction_id:
                    transaction = db.query(Transaction).filter(
                        Transaction.transaction_id == book_request.transaction_id,
                        Transaction.status == 'BORROWED'
                    ).first()
                    
                    if transaction:
                        return_date = datetime.utcnow()
                        transaction.return_date = return_date
                        transaction.status = 'RETURNED'
                        
                        # Calculate fine if overdue
                        if transaction.due_date and return_date > transaction.due_date:
                            days_overdue = (return_date - transaction.due_date).days
                            transaction.fine_amount = days_overdue * 10
                        
                        # Update book availability
                        book = db.query(Book).filter(Book.book_id == transaction.book_id).first()
                        if book:
                            book.available_copies += 1
                    else:
                        return library_service_pb2.BookRequestResponse(
                            success=False,
                            message="Transaction not found or already returned"
                        )
            
            # Update request status
            book_request.status = 'APPROVED'
            book_request.admin_response_date = datetime.utcnow()
            book_request.admin_id = request.admin_id
            
            db.commit()
            logger.info(f"Book request approved successfully: request_id={request.request_id}, type={book_request.request_type}")
            
            return library_service_pb2.BookRequestResponse(
                success=True,
                message="Request approved successfully"
            )
        except Exception as e:
            logger.error(f"Error approving book request: request_id={request.request_id} - {str(e)}")
            db.rollback()
            return library_service_pb2.BookRequestResponse(
                success=False,
                message=str(e)
            )
        finally:
            db.close()
    
    def RejectBookRequest(self, request, context):
        db = SessionLocal()
        try:
            book_request = db.query(BookRequest).filter(
                BookRequest.request_id == request.request_id,
                BookRequest.status == 'PENDING'
            ).first()
            
            if not book_request:
                return library_service_pb2.BookRequestResponse(
                    success=False,
                    message="Request not found or already processed"
                )
            
            book_request.status = 'REJECTED'
            book_request.admin_response_date = datetime.utcnow()
            book_request.admin_id = request.admin_id
            
            db.commit()
            
            return library_service_pb2.BookRequestResponse(
                success=True,
                message="Request rejected successfully"
            )
        except Exception as e:
            db.rollback()
            return library_service_pb2.BookRequestResponse(
                success=False,
                message=str(e)
            )
        finally:
            db.close()
    
    def GetUserStats(self, request, context):
        db = SessionLocal()
        try:
            user_id = request.user_id
            
            # Total books taken (all time)
            total_taken = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == 'BORROW'
            ).count()
            
            # Currently borrowed books
            currently_borrowed = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.status == 'BORROWED'
            ).count()
            
            # Overdue books with fines
            overdue_transactions = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.status == 'BORROWED',
                Transaction.due_date < datetime.utcnow()
            ).all()
            
            total_overdue = len(overdue_transactions)
            total_fine = sum(max(0, (datetime.utcnow() - txn.due_date).days * 10) for txn in overdue_transactions)
            
            return library_service_pb2.UserStatsResponse(
                total_books_taken=total_taken,
                currently_borrowed=currently_borrowed,
                overdue_books=total_overdue,
                total_fine=total_fine
            )
        finally:
            db.close()
    
    def GetUserTransactions(self, request, context):
        db = SessionLocal()
        try:
            query = db.query(Transaction).filter(Transaction.user_id == request.user_id)
            
            if request.status:
                query = query.filter(Transaction.status == request.status)
            
            transactions = query.order_by(Transaction.transaction_date.desc()).all()
            transaction_list = []
            
            for txn in transactions:
                # Get book details
                book = db.query(Book).filter(Book.book_id == txn.book_id).first()
                
                # Calculate current fine for overdue books
                current_fine = txn.fine_amount or 0
                if txn.status == 'BORROWED' and txn.due_date and datetime.utcnow() > txn.due_date:
                    days_overdue = (datetime.utcnow() - txn.due_date).days
                    current_fine = days_overdue * 10
                
                transaction_list.append(library_service_pb2.UserTransaction(
                    transaction_id=txn.transaction_id,
                    book_id=txn.book_id,
                    book_title=book.title if book else "Unknown",
                    book_author=book.author if book else "Unknown",
                    transaction_type=txn.transaction_type,
                    transaction_date=txn.transaction_date.isoformat() if txn.transaction_date else "",
                    due_date=txn.due_date.isoformat() if txn.due_date else "",
                    return_date=txn.return_date.isoformat() if txn.return_date else "",
                    status=txn.status,
                    fine_amount=current_fine
                ))
            
            return library_service_pb2.GetUserTransactionsResponse(transactions=transaction_list)
        finally:
            db.close()
    
    def CreateBook(self, request, context):
        db = SessionLocal()
        try:
            book = Book(
                title=request.title,
                author=request.author,
                genre=request.genre,
                published_year=request.published_year,
                available_copies=request.available_copies,
                is_deleted=False
            )
            db.add(book)
            db.commit()
            
            return library_service_pb2.BookResponse(
                success=True,
                book=library_service_pb2.Book(
                    book_id=book.book_id,
                    title=book.title,
                    author=book.author,
                    genre=book.genre,
                    published_year=book.published_year,
                    available_copies=book.available_copies,
                    is_deleted=book.is_deleted
                ),
                message="Book created successfully"
            )
        except Exception as e:
            db.rollback()
            return library_service_pb2.BookResponse(
                success=False,
                message=str(e)
            )
        finally:
            db.close()
    
    def UpdateBook(self, request, context):
        db = SessionLocal()
        try:
            book = db.query(Book).filter(Book.book_id == request.book_id, Book.is_deleted.is_(False)).first()
            if not book:
                return library_service_pb2.BookResponse(
                    success=False,
                    message="Book not found"
                )
            
            book.title = request.title
            book.author = request.author
            book.genre = request.genre
            book.published_year = request.published_year
            book.available_copies = request.available_copies
            db.commit()
            
            return library_service_pb2.BookResponse(
                success=True,
                book=library_service_pb2.Book(
                    book_id=book.book_id,
                    title=book.title,
                    author=book.author,
                    genre=book.genre,
                    published_year=book.published_year,
                    available_copies=book.available_copies,
                    is_deleted=book.is_deleted
                ),
                message="Book updated successfully"
            )
        except Exception as e:
            db.rollback()
            return library_service_pb2.BookResponse(
                success=False,
                message=str(e)
            )
        finally:
            db.close()
    
    def DeleteBook(self, request, context):
        db = SessionLocal()
        try:
            book = db.query(Book).filter(Book.book_id == request.book_id, Book.is_deleted.is_(False)).first()
            if not book:
                return library_service_pb2.BookResponse(
                    success=False,
                    message="Book not found"
                )
            
            # Soft delete
            book.is_deleted = True
            db.commit()
            
            return library_service_pb2.BookResponse(
                success=True,
                message="Book deleted successfully"
            )
        except Exception as e:
            db.rollback()
            return library_service_pb2.BookResponse(
                success=False,
                message=str(e)
            )
        finally:
            db.close()
    
    def CreateUser(self, request, context):
        db = SessionLocal()
        try:
            password_hash = hashlib.sha256(request.password.encode()).hexdigest()
            user = User(
                username=request.username,
                email=request.email,
                password_hash=password_hash,
                role=request.role,
                is_active=True
            )
            db.add(user)
            db.commit()
            
            return library_service_pb2.UserResponse(
                success=True,
                user=library_service_pb2.User(
                    user_id=user.user_id,
                    username=user.username,
                    email=user.email,
                    role=user.role,
                    is_active=user.is_active
                ),
                message="User created successfully"
            )
        except Exception as e:
            db.rollback()
            return library_service_pb2.UserResponse(
                success=False,
                message=str(e)
            )
        finally:
            db.close()
    
    def UpdateUser(self, request, context):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_id == request.user_id).first()
            if not user:
                return library_service_pb2.UserResponse(
                    success=False,
                    message="User not found"
                )
            
            user.username = request.username
            user.email = request.email
            user.role = request.role
            user.is_active = request.is_active
            
            if request.password:
                user.password_hash = hashlib.sha256(request.password.encode()).hexdigest()
            
            db.commit()
            
            return library_service_pb2.UserResponse(
                success=True,
                user=library_service_pb2.User(
                    user_id=user.user_id,
                    username=user.username,
                    email=user.email,
                    role=user.role,
                    is_active=user.is_active
                ),
                message="User updated successfully"
            )
        except Exception as e:
            db.rollback()
            return library_service_pb2.UserResponse(
                success=False,
                message=str(e)
            )
        finally:
            db.close()