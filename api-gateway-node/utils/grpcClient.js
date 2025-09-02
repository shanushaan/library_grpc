const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const path = require('path');

// Load protobuf
const PROTO_PATH = path.join(__dirname, '../proto/library_service.proto');
const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true
});

const libraryProto = grpc.loadPackageDefinition(packageDefinition).library;

// gRPC client
const grpcHost = process.env.GRPC_SERVER_HOST || 'localhost';
const grpcPort = process.env.GRPC_SERVER_PORT || '50051';
const client = new libraryProto.LibraryService(`${grpcHost}:${grpcPort}`, grpc.credentials.createInsecure());

// Helper function to promisify gRPC calls
const grpcCall = (method, request) => {
  return new Promise((resolve, reject) => {
    client[method](request, (error, response) => {
      if (error) reject(error);
      else resolve(response);
    });
  });
};

module.exports = { grpcCall };