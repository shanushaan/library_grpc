import logging
import psycopg2
from connection_pool import db_pool
import library_service_pb2

logger = logging.getLogger(__name__)

class BookService:
    
    def get_books(self, request, context):
        """Get books with optional search query"""
        try:
            with db_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    if request.search_query:
                        cursor.execute(
                            "SELECT book_id, title, author, genre, published_year, available_copies, is_deleted FROM books WHERE is_deleted = false AND (title ILIKE %s OR author ILIKE %s OR genre ILIKE %s)",
                            (f"%{request.search_query}%", f"%{request.search_query}%", f"%{request.search_query}%")
                        )
                    else:
                        cursor.execute(
                            "SELECT book_id, title, author, genre, published_year, available_copies, is_deleted FROM books WHERE is_deleted = false"
                        )
                    
                    books_data = cursor.fetchall()
                    book_list = []
                    
                    for book_data in books_data:
                        book_list.append(library_service_pb2.Book(
                            book_id=book_data[0],
                            title=book_data[1],
                            author=book_data[2] or "",
                            genre=book_data[3] or "",
                            published_year=book_data[4] or 0,
                            available_copies=book_data[5],
                            is_deleted=book_data[6] or False
                        ))
                    
                    return library_service_pb2.GetBooksResponse(books=book_list)
        except psycopg2.DatabaseError as e:
            logger.error(f"Database error fetching books: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching books: {e}")
            raise
    
    def create_book(self, request, context):
        """Create a new book"""
        try:
            with db_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO books (title, author, genre, published_year, available_copies, is_deleted) VALUES (%s, %s, %s, %s, %s, %s) RETURNING book_id",
                        (request.title, request.author, request.genre, request.published_year, request.available_copies, False)
                    )
                    book_id = cursor.fetchone()[0]
                    conn.commit()
                    
                    return library_service_pb2.BookResponse(
                        success=True,
                        book=library_service_pb2.Book(
                            book_id=book_id,
                            title=request.title,
                            author=request.author,
                            genre=request.genre,
                            published_year=request.published_year,
                            available_copies=request.available_copies,
                            is_deleted=False
                        ),
                        message="Book created successfully"
                    )
        except psycopg2.DatabaseError as e:
            logger.error(f"Database error creating book: {e}")
            return library_service_pb2.BookResponse(success=False, message="Database error occurred")
        except Exception as e:
            logger.error(f"Error creating book: {e}")
            return library_service_pb2.BookResponse(success=False, message="Internal server error")
    
    def update_book(self, request, context):
        """Update an existing book"""
        try:
            with db_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE books SET title = %s, author = %s, genre = %s, published_year = %s, available_copies = %s WHERE book_id = %s AND is_deleted = false",
                        (request.title, request.author, request.genre, request.published_year, request.available_copies, request.book_id)
                    )
                    
                    if cursor.rowcount == 0:
                        return library_service_pb2.BookResponse(success=False, message="Book not found")
                    
                    conn.commit()
                    return library_service_pb2.BookResponse(
                        success=True,
                        book=library_service_pb2.Book(
                            book_id=request.book_id,
                            title=request.title,
                            author=request.author,
                            genre=request.genre,
                            published_year=request.published_year,
                            available_copies=request.available_copies,
                            is_deleted=False
                        ),
                        message="Book updated successfully"
                    )
        except psycopg2.DatabaseError as e:
            logger.error(f"Database error updating book: {e}")
            return library_service_pb2.BookResponse(success=False, message="Database error occurred")
        except Exception as e:
            logger.error(f"Error updating book: {e}")
            return library_service_pb2.BookResponse(success=False, message="Internal server error")
    
    def delete_book(self, request, context):
        """Soft delete a book"""
        try:
            with db_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE books SET is_deleted = true WHERE book_id = %s AND is_deleted = false",
                        (request.book_id,)
                    )
                    
                    if cursor.rowcount == 0:
                        return library_service_pb2.BookResponse(success=False, message="Book not found")
                    
                    conn.commit()
                    return library_service_pb2.BookResponse(success=True, message="Book deleted successfully")
        except psycopg2.DatabaseError as e:
            logger.error(f"Database error deleting book: {e}")
            return library_service_pb2.BookResponse(success=False, message="Database error occurred")
        except Exception as e:
            logger.error(f"Error deleting book: {e}")
            return library_service_pb2.BookResponse(success=False, message="Internal server error")