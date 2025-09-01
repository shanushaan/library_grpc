FROM python:3.10-slim

WORKDIR /app

# Copy proto files for gRPC client
COPY proto/ ./proto/

# Copy service-specific files
COPY api-gateway/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY api-gateway/ ./api-gateway/

# Generate proto files for gRPC client
RUN python -m grpc_tools.protoc --proto_path=proto --python_out=api-gateway --grpc_python_out=api-gateway proto/library_service.proto

EXPOSE 8001

CMD ["python", "api-gateway/gateway.py"]