# Setup Instructions

## Prerequisites

1. **Docker**: Install Docker Desktop
   - Windows: https://docs.docker.com/desktop/windows/install/
   - macOS: https://docs.docker.com/desktop/mac/install/
   - Linux: https://docs.docker.com/engine/install/

2. **Docker Compose**: Usually included with Docker Desktop

## Quick Setup

1. **Download/Clone the project**
```bash
git clone <repository-url>
cd library-grpc-service
```

2. **Start the application**
```bash
docker-compose up -d
```

3. **Wait for services to start** (30-60 seconds)
   - Check status: `docker-compose ps`
   - All services should show "Up" status

4. **Access the application**
   - Open browser: http://localhost:3000
   - Login with: admin/admin123 or john_user/user123

## Troubleshooting

### Port Conflicts
If ports are already in use, modify `docker-compose.yml`:
```yaml
ports:
  - "3001:3000"  # Change 3000 to 3001
  - "8002:8001"  # Change 8001 to 8002
```

### Services Not Starting
```bash
# Check logs
docker-compose logs

# Restart services
docker-compose down
docker-compose up -d
```

### Database Issues
```bash
# Reset database
docker-compose down -v
docker-compose up -d
```

## Manual Build (if needed)

```bash
# Build all services
docker-compose build

# Start with build
docker-compose up --build -d
```

## Stopping the Application

```bash
# Stop services
docker-compose down

# Stop and remove volumes (reset database)
docker-compose down -v
```