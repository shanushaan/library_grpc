import logging
from datetime import datetime, timedelta
import psycopg2
from connection_pool import db_pool
import library_service_pb2

logger = logging.getLogger(__name__)

class RequestService:
    
    def create_book_request(self, request, context):
        """Create a new book request"""
        logger.info("Creating book request", extra={"user_id": request.user_id, "book_id": request.book_id, "request_type": request.request_type})
        try:
            with db_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO book_requests (user_id, book_id, request_type, status, notes, transaction_id) VALUES (%s, %s, %s, %s, %s, %s) RETURNING request_id",
                        (request.user_id, request.book_id, request.request_type, 'PENDING', request.notes, request.transaction_id if request.transaction_id else None)
                    )
                    request_id = cursor.fetchone()[0]
                    conn.commit()
                    
                    logger.info("Book request created successfully", extra={"request_id": request_id, "user_id": request.user_id, "book_id": request.book_id})
                    
                    return library_service_pb2.BookRequestResponse(
                        success=True,
                        request=library_service_pb2.BookRequest(
                            request_id=request_id,
                            user_id=request.user_id,
                            book_id=request.book_id,
                            request_type=request.request_type,
                            status='PENDING'
                        ),
                        message="Request created successfully"
                    )
        except psycopg2.DatabaseError as e:
            logger.error("Database error creating book request", extra={"user_id": request.user_id, "book_id": request.book_id, "error": str(e)})
            return library_service_pb2.BookRequestResponse(success=False, message="Database error occurred")
        except Exception as e:
            logger.error("Error creating book request", extra={"user_id": request.user_id, "book_id": request.book_id, "error": str(e)})
            return library_service_pb2.BookRequestResponse(success=False, message="Internal server error")
    
    def get_book_requests(self, request, context):
        """Get book requests with optional status filter"""
        try:
            with db_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    if request.status:
                        cursor.execute(
                            "SELECT request_id, user_id, book_id, request_type, status, request_date, notes, transaction_id FROM book_requests WHERE status = %s ORDER BY request_date DESC",
                            (request.status,)
                        )
                    else:
                        cursor.execute(
                            "SELECT request_id, user_id, book_id, request_type, status, request_date, notes, transaction_id FROM book_requests ORDER BY request_date DESC"
                        )
                    
                    requests_data = cursor.fetchall()
                    request_list = []
                    
                    for req_data in requests_data:
                        request_list.append(library_service_pb2.BookRequest(
                            request_id=req_data[0],
                            user_id=req_data[1],
                            book_id=req_data[2],
                            request_type=req_data[3],
                            status=req_data[4],
                            request_date=req_data[5].isoformat() if req_data[5] else "",
                            notes=req_data[6] or "",
                            transaction_id=req_data[7] or 0
                        ))
                    
                    return library_service_pb2.GetBookRequestsResponse(requests=request_list)
        except psycopg2.DatabaseError as e:
            logger.error(f"Database error fetching book requests: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching book requests: {e}")
            raise
    
    def approve_book_request(self, request, context):
        """Approve a pending book request"""
        logger.info(f"Approving book request: request_id={request.request_id}")
        try:
            with db_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Get request details
                    cursor.execute(
                        "SELECT user_id, book_id, request_type, transaction_id FROM book_requests WHERE request_id = %s AND status = 'PENDING'",
                        (request.request_id,)
                    )
                    req_data = cursor.fetchone()
                    if not req_data:
                        return library_service_pb2.BookRequestResponse(success=False, message="Request not found or already processed")
                    
                    user_id, book_id, request_type, transaction_id = req_data
                    
                    # Process based on request type
                    if request_type == 'ISSUE':
                        # Check book availability
                        cursor.execute("SELECT available_copies FROM books WHERE book_id = %s", (book_id,))
                        book_data = cursor.fetchone()
                        if not book_data or book_data[0] <= 0:
                            return library_service_pb2.BookRequestResponse(success=False, message="Book no longer available")
                        
                        # Create transaction
                        cursor.execute(
                            "INSERT INTO transactions (user_id, book_id, transaction_type, transaction_date, due_date, status, fine_amount) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                            (user_id, book_id, 'BORROW', datetime.utcnow(), datetime.utcnow() + timedelta(days=30), 'BORROWED', 0)
                        )
                        cursor.execute("UPDATE books SET available_copies = available_copies - 1 WHERE book_id = %s", (book_id,))
                        
                    elif request_type == 'RETURN' and transaction_id:
                        # Return book
                        return_date = datetime.utcnow()
                        cursor.execute(
                            "SELECT due_date, book_id FROM transactions WHERE transaction_id = %s AND status = 'BORROWED'",
                            (transaction_id,)
                        )
                        txn_data = cursor.fetchone()
                        if txn_data:
                            fine_amount = 0
                            if txn_data[0] and return_date > txn_data[0]:
                                days_overdue = (return_date - txn_data[0]).days
                                fine_amount = days_overdue * 10
                            
                            cursor.execute(
                                "UPDATE transactions SET return_date = %s, status = 'RETURNED', fine_amount = %s WHERE transaction_id = %s",
                                (return_date, fine_amount, transaction_id)
                            )
                            cursor.execute("UPDATE books SET available_copies = available_copies + 1 WHERE book_id = %s", (txn_data[1],))
                    
                    # Update request status
                    cursor.execute(
                        "UPDATE book_requests SET status = 'APPROVED', admin_response_date = %s, admin_id = %s WHERE request_id = %s",
                        (datetime.utcnow(), request.admin_id, request.request_id)
                    )
                    conn.commit()
                    
                    logger.info(f"Book request approved successfully: request_id={request.request_id}, type={request_type}")
                    return library_service_pb2.BookRequestResponse(success=True, message="Request approved successfully")
                    
        except psycopg2.DatabaseError as e:
            logger.error(f"Database error approving book request: request_id={request.request_id} - {str(e)}")
            return library_service_pb2.BookRequestResponse(success=False, message="Database error occurred")
        except Exception as e:
            logger.error(f"Error approving book request: request_id={request.request_id} - {str(e)}")
            return library_service_pb2.BookRequestResponse(success=False, message="Internal server error")
    
    def reject_book_request(self, request, context):
        """Reject a pending book request"""
        try:
            with db_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE book_requests SET status = 'REJECTED', admin_response_date = %s, admin_id = %s WHERE request_id = %s AND status = 'PENDING'",
                        (datetime.utcnow(), request.admin_id, request.request_id)
                    )
                    
                    if cursor.rowcount == 0:
                        return library_service_pb2.BookRequestResponse(success=False, message="Request not found or already processed")
                    
                    conn.commit()
                    return library_service_pb2.BookRequestResponse(success=True, message="Request rejected successfully")
                    
        except psycopg2.DatabaseError as e:
            logger.error(f"Database error rejecting book request: {e}")
            return library_service_pb2.BookRequestResponse(success=False, message="Database error occurred")
        except Exception as e:
            logger.error(f"Error rejecting book request: {e}")
            return library_service_pb2.BookRequestResponse(success=False, message="Internal server error")