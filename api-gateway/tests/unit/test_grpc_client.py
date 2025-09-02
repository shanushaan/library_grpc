import pytest
from unittest.mock import patch, AsyncMock
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core.grpc_client import get_grpc_client

pytestmark = pytest.mark.asyncio

class TestGrpcClient:
    """Test gRPC client connection functionality"""
    
    @patch('core.grpc_client.grpc.aio.insecure_channel')
    @patch('core.grpc_client.library_service_pb2_grpc.LibraryServiceStub')
    async def test_get_grpc_client_default_config(self, mock_stub, mock_channel):
        mock_stub.return_value = AsyncMock()
        
        client = await get_grpc_client()
        
        mock_channel.assert_called_once_with('localhost:50051')
        mock_stub.assert_called_once()
        assert client is not None
    
    @patch.dict(os.environ, {'GRPC_SERVER_HOST': 'testhost', 'GRPC_SERVER_PORT': '9999'})
    @patch('core.grpc_client.grpc.aio.insecure_channel')
    @patch('core.grpc_client.library_service_pb2_grpc.LibraryServiceStub')
    async def test_get_grpc_client_custom_config(self, mock_stub, mock_channel):
        mock_stub.return_value = AsyncMock()
        
        client = await get_grpc_client()
        
        mock_channel.assert_called_once_with('testhost:9999')
        mock_stub.assert_called_once()
        assert client is not None