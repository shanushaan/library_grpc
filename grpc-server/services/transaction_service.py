import logging
from datetime import datetime, timedelta
import psycopg2
from connection_pool import db_pool
import library_service_pb2

logger = logging.getLogger(__name__)

class TransactionService:
    
    def get_transactions(self, request, context):
        """Get transactions with optional filters"""
        try:
            with db_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = "SELECT transaction_id, user_id, book_id, transaction_type, transaction_date, due_date, return_date, status, fine_amount FROM transactions"
                    params = []
                    conditions = []
                    
                    if request.user_id:
                        conditions.append("user_id = %s")
                        params.append(request.user_id)
                    if request.status:
                        conditions.append("status = %s")
                        params.append(request.status)
                    
                    if conditions:
                        query += " WHERE " + " AND ".join(conditions)
                    query += " ORDER BY transaction_date DESC"
                    
                    cursor.execute(query, params)
                    transactions_data = cursor.fetchall()
                    transaction_list = []
                    
                    for txn_data in transactions_data:
                        transaction_list.append(library_service_pb2.Transaction(
                            transaction_id=txn_data[0],
                            member_id=txn_data[1],
                            book_id=txn_data[2],
                            transaction_type=txn_data[3],
                            transaction_date=txn_data[4].isoformat() if txn_data[4] else "",
                            due_date=txn_data[5].isoformat() if txn_data[5] else "",
                            return_date=txn_data[6].isoformat() if txn_data[6] else "",
                            status=txn_data[7],
                            fine_amount=txn_data[8] or 0
                        ))
                    
                    return library_service_pb2.GetTransactionsResponse(transactions=transaction_list)
        except psycopg2.DatabaseError as e:
            logger.error(f"Database error fetching transactions: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching transactions: {e}")
            raise
    
    def issue_book(self, request, context):
        """Issue a book to a user"""
        try:
            with db_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Check book availability
                    cursor.execute("SELECT available_copies FROM books WHERE book_id = %s", (request.book_id,))
                    book_data = cursor.fetchone()
                    if not book_data or book_data[0] <= 0:
                        return library_service_pb2.TransactionResponse(success=False, message="Book not available")
                    
                    # Check user exists
                    cursor.execute("SELECT role FROM users WHERE user_id = %s", (request.member_id,))
                    user_data = cursor.fetchone()
                    if not user_data:
                        return library_service_pb2.TransactionResponse(success=False, message="User not found")
                    
                    # Check existing borrow
                    cursor.execute(
                        "SELECT COUNT(*) FROM transactions WHERE user_id = %s AND book_id = %s AND status = 'BORROWED'",
                        (request.member_id, request.book_id)
                    )
                    if cursor.fetchone()[0] > 0:
                        return library_service_pb2.TransactionResponse(success=False, message="User already has this book borrowed")
                    
                    # Check borrowing limit for regular users
                    if user_data[0] == 'user':
                        cursor.execute(
                            "SELECT COUNT(*) FROM transactions WHERE user_id = %s AND status = 'BORROWED'",
                            (request.member_id,)
                        )
                        if cursor.fetchone()[0] >= 3:
                            return library_service_pb2.TransactionResponse(success=False, message="User already has 3 books borrowed")
                    
                    # Create transaction
                    cursor.execute(
                        "INSERT INTO transactions (user_id, book_id, transaction_type, transaction_date, due_date, status, fine_amount) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING transaction_id",
                        (request.member_id, request.book_id, 'BORROW', datetime.utcnow(), datetime.utcnow() + timedelta(days=30), 'BORROWED', 0)
                    )
                    transaction_id = cursor.fetchone()[0]
                    
                    # Update book availability
                    cursor.execute("UPDATE books SET available_copies = available_copies - 1 WHERE book_id = %s", (request.book_id,))
                    conn.commit()
                    
                    return library_service_pb2.TransactionResponse(
                        success=True,
                        transaction=library_service_pb2.Transaction(
                            transaction_id=transaction_id,
                            member_id=request.member_id,
                            book_id=request.book_id,
                            transaction_type='BORROW',
                            status='BORROWED'
                        ),
                        message="Book issued successfully"
                    )
        except psycopg2.DatabaseError as e:
            logger.error(f"Database error issuing book: {e}")
            return library_service_pb2.TransactionResponse(success=False, message="Database error occurred")
        except Exception as e:
            logger.error(f"Error issuing book: {e}")
            return library_service_pb2.TransactionResponse(success=False, message="Internal server error")
    
    def return_book(self, request, context):
        """Return a borrowed book"""
        try:
            with db_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Get transaction
                    cursor.execute(
                        "SELECT book_id, due_date FROM transactions WHERE transaction_id = %s AND status = 'BORROWED'",
                        (request.transaction_id,)
                    )
                    txn_data = cursor.fetchone()
                    if not txn_data:
                        return library_service_pb2.TransactionResponse(success=False, message="Transaction not found or book already returned")
                    
                    # Calculate fine
                    return_date = datetime.utcnow()
                    fine_amount = 0
                    if txn_data[1] and return_date > txn_data[1]:
                        days_overdue = (return_date - txn_data[1]).days
                        fine_amount = days_overdue * 10
                    
                    # Update transaction
                    cursor.execute(
                        "UPDATE transactions SET return_date = %s, status = 'RETURNED', fine_amount = %s WHERE transaction_id = %s",
                        (return_date, fine_amount, request.transaction_id)
                    )
                    
                    # Update book availability
                    cursor.execute("UPDATE books SET available_copies = available_copies + 1 WHERE book_id = %s", (txn_data[0],))
                    conn.commit()
                    
                    return library_service_pb2.TransactionResponse(
                        success=True,
                        transaction=library_service_pb2.Transaction(
                            transaction_id=request.transaction_id,
                            book_id=txn_data[0],
                            transaction_type='RETURN',
                            status='RETURNED',
                            fine_amount=fine_amount
                        ),
                        message="Book returned successfully"
                    )
        except psycopg2.DatabaseError as e:
            logger.error(f"Database error returning book: {e}")
            return library_service_pb2.TransactionResponse(success=False, message="Database error occurred")
        except Exception as e:
            logger.error(f"Error returning book: {e}")
            return library_service_pb2.TransactionResponse(success=False, message="Internal server error")