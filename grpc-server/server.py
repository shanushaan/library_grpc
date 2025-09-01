import grpc
from concurrent import futures
import sys
import os

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.models import User, Book, Transaction, BookRequest
from shared.database import SessionLocal, engine
from services.library_service import LibraryServiceImpl

# Import pre-generated proto files
import library_service_pb2_grpc

def serve():
    try:
        print("Initializing gRPC server...")
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        
        print("Adding service to server...")
        library_service_pb2_grpc.add_LibraryServiceServicer_to_server(
            LibraryServiceImpl(), server
        )
        
        listen_addr = '[::]:50051'
        print(f"Binding to {listen_addr}...")
        server.add_insecure_port(listen_addr)
        
        print(f"Starting gRPC server on {listen_addr}")
        server.start()
        print("gRPC server started successfully!")
        server.wait_for_termination()
    except Exception as e:
        print(f"Error starting gRPC server: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    serve()