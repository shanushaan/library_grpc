import grpc.aio
import os
import library_service_pb2_grpc

# Async gRPC client connection
async def get_grpc_client():
    grpc_host = os.getenv('GRPC_SERVER_HOST', 'localhost')
    grpc_port = os.getenv('GRPC_SERVER_PORT', '50051')
    channel = grpc.aio.insecure_channel(f'{grpc_host}:{grpc_port}')
    return library_service_pb2_grpc.LibraryServiceStub(channel)