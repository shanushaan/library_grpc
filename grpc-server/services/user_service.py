import hashlib
import logging
from datetime import datetime
import psycopg2
from connection_pool import db_pool
import library_service_pb2

logger = logging.getLogger(__name__)

class UserService:
    
    def get_users(self, request, context):
        """Get all users"""
        try:
            with db_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT user_id, username, email, role, is_active FROM users")
                    users_data = cursor.fetchall()
                    user_list = []
                    
                    for user_data in users_data:
                        user_list.append(library_service_pb2.User(
                            user_id=user_data[0],
                            username=user_data[1],
                            email=user_data[2],
                            role=user_data[3],
                            is_active=user_data[4]
                        ))
                    
                    return library_service_pb2.GetUsersResponse(users=user_list)
        except psycopg2.DatabaseError as e:
            logger.error(f"Database error fetching users: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching users: {e}")
            raise
    
    def create_user(self, request, context):
        """Create a new user"""
        try:
            with db_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    password_hash = hashlib.sha256(request.password.encode()).hexdigest()
                    cursor.execute(
                        "INSERT INTO users (username, email, password_hash, role, is_active) VALUES (%s, %s, %s, %s, %s) RETURNING user_id",
                        (request.username, request.email, password_hash, request.role, True)
                    )
                    user_id = cursor.fetchone()[0]
                    conn.commit()
                    
                    return library_service_pb2.UserResponse(
                        success=True,
                        user=library_service_pb2.User(
                            user_id=user_id,
                            username=request.username,
                            email=request.email,
                            role=request.role,
                            is_active=True
                        ),
                        message="User created successfully"
                    )
        except psycopg2.DatabaseError as e:
            logger.error(f"Database error creating user: {e}")
            return library_service_pb2.UserResponse(success=False, message="Database error occurred")
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return library_service_pb2.UserResponse(success=False, message="Internal server error")
    
    def update_user(self, request, context):
        """Update an existing user"""
        try:
            with db_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    if request.password:
                        password_hash = hashlib.sha256(request.password.encode()).hexdigest()
                        cursor.execute(
                            "UPDATE users SET username = %s, email = %s, role = %s, is_active = %s, password_hash = %s WHERE user_id = %s",
                            (request.username, request.email, request.role, request.is_active, password_hash, request.user_id)
                        )
                    else:
                        cursor.execute(
                            "UPDATE users SET username = %s, email = %s, role = %s, is_active = %s WHERE user_id = %s",
                            (request.username, request.email, request.role, request.is_active, request.user_id)
                        )
                    
                    if cursor.rowcount == 0:
                        return library_service_pb2.UserResponse(success=False, message="User not found")
                    
                    conn.commit()
                    return library_service_pb2.UserResponse(
                        success=True,
                        user=library_service_pb2.User(
                            user_id=request.user_id,
                            username=request.username,
                            email=request.email,
                            role=request.role,
                            is_active=request.is_active
                        ),
                        message="User updated successfully"
                    )
        except psycopg2.DatabaseError as e:
            logger.error(f"Database error updating user: {e}")
            return library_service_pb2.UserResponse(success=False, message="Database error occurred")
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return library_service_pb2.UserResponse(success=False, message="Internal server error")
    
    def get_user_stats(self, request, context):
        """Get user statistics"""
        try:
            with db_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    user_id = request.user_id
                    
                    # Total books taken
                    cursor.execute(
                        "SELECT COUNT(*) FROM transactions WHERE user_id = %s AND transaction_type = 'BORROW'",
                        (user_id,)
                    )
                    total_taken = cursor.fetchone()[0]
                    
                    # Currently borrowed
                    cursor.execute(
                        "SELECT COUNT(*) FROM transactions WHERE user_id = %s AND status = 'BORROWED'",
                        (user_id,)
                    )
                    currently_borrowed = cursor.fetchone()[0]
                    
                    # Overdue books
                    cursor.execute(
                        "SELECT COUNT(*), COALESCE(SUM(GREATEST(0, (EXTRACT(EPOCH FROM (NOW() - due_date)) / 86400)::int * 10)), 0) FROM transactions WHERE user_id = %s AND status = 'BORROWED' AND due_date < NOW()",
                        (user_id,)
                    )
                    overdue_data = cursor.fetchone()
                    total_overdue = overdue_data[0]
                    total_fine = int(overdue_data[1])
                    
                    return library_service_pb2.UserStatsResponse(
                        total_books_taken=total_taken,
                        currently_borrowed=currently_borrowed,
                        overdue_books=total_overdue,
                        total_fine=total_fine
                    )
        except psycopg2.DatabaseError as e:
            logger.error(f"Database error fetching user stats: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching user stats: {e}")
            raise
    
    def get_user_transactions(self, request, context):
        """Get user transactions with book details"""
        try:
            with db_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        SELECT t.transaction_id, t.book_id, b.title, b.author, t.transaction_type, 
                               t.transaction_date, t.due_date, t.return_date, t.status, t.fine_amount
                        FROM transactions t
                        LEFT JOIN books b ON t.book_id = b.book_id
                        WHERE t.user_id = %s
                    """
                    params = [request.user_id]
                    
                    if request.status:
                        query += " AND t.status = %s"
                        params.append(request.status)
                    
                    query += " ORDER BY t.transaction_date DESC"
                    
                    cursor.execute(query, params)
                    transactions_data = cursor.fetchall()
                    transaction_list = []
                    
                    for txn_data in transactions_data:
                        # Calculate current fine for overdue books
                        current_fine = txn_data[9] or 0
                        if txn_data[8] == 'BORROWED' and txn_data[6] and datetime.utcnow() > txn_data[6]:
                            days_overdue = (datetime.utcnow() - txn_data[6]).days
                            current_fine = days_overdue * 10
                        
                        transaction_list.append(library_service_pb2.UserTransaction(
                            transaction_id=txn_data[0],
                            book_id=txn_data[1],
                            book_title=txn_data[2] if txn_data[2] else "Unknown",
                            book_author=txn_data[3] if txn_data[3] else "Unknown",
                            transaction_type=txn_data[4],
                            transaction_date=txn_data[5].isoformat() if txn_data[5] else "",
                            due_date=txn_data[6].isoformat() if txn_data[6] else "",
                            return_date=txn_data[7].isoformat() if txn_data[7] else "",
                            status=txn_data[8],
                            fine_amount=current_fine
                        ))
                    
                    return library_service_pb2.GetUserTransactionsResponse(transactions=transaction_list)
        except psycopg2.DatabaseError as e:
            logger.error(f"Database error fetching user transactions: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching user transactions: {e}")
            raise