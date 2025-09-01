FROM python:3.10-slim

WORKDIR /app

# Copy shared dependencies first
COPY shared/ ./shared/
COPY proto/ ./proto/

# Copy service-specific files
COPY grpc-server/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY grpc-server/ ./grpc-server/

# Generate proto files
RUN python -m grpc_tools.protoc --proto_path=proto --python_out=grpc-server --grpc_python_out=grpc-server proto/library_service.proto

EXPOSE 50051

CMD ["python", "grpc-server/server.py"]