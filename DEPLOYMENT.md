# Library Management System - Deployment Guide

## 🌐 Production Deployment

### Environment Setup

**1. Server Requirements**
- **OS**: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 50GB minimum
- **CPU**: 4 cores minimum
- **Network**: Stable internet connection

**2. Install Dependencies**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### Production Configuration

**1. Environment Variables**
```bash
# Create production environment file
cat > .env.prod << EOF
# Database Configuration
POSTGRES_DB=library_db
POSTGRES_USER=library_user
POSTGRES_PASSWORD=your_secure_password_here

# API Gateway Configuration
API_GATEWAY_PORT=8001
FRONTEND_PORT=3000

# Security
JWT_SECRET=your_jwt_secret_here
CORS_ORIGINS=https://yourdomain.com

# Logging
LOG_LEVEL=INFO
EOF
```

**2. Production Docker Compose**
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./db-init/00_complete_init.sql:/docker-entrypoint-initdb.d/00_complete_init.sql
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 30s
      timeout: 10s
      retries: 3

  grpc-server:
    build: 
      context: .
      dockerfile: grpc-server/Dockerfile
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped
    environment:
      - LOG_LEVEL=${LOG_LEVEL}

  api-gateway-node:
    build:
      context: .
      dockerfile: api-gateway-node/Dockerfile
    ports:
      - "${API_GATEWAY_PORT}:8001"
    depends_on:
      - grpc-server
    restart: unless-stopped
    environment:
      - NODE_ENV=production

  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    ports:
      - "${FRONTEND_PORT}:3000"
    depends_on:
      - api-gateway-node
    restart: unless-stopped
    environment:
      - NODE_ENV=production

volumes:
  postgres_data:

networks:
  default:
    driver: bridge
```

### SSL/TLS Configuration

**1. Nginx Reverse Proxy**
```nginx
# /etc/nginx/sites-available/library-system
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API Gateway
    location /api/ {
        proxy_pass http://localhost:8001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**2. Enable Nginx Configuration**
```bash
sudo ln -s /etc/nginx/sites-available/library-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Database Security

**1. Secure PostgreSQL**
```bash
# Create dedicated database user
docker exec -it library_grpc-postgres-1 psql -U postgres -c "
CREATE USER library_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE library_db TO library_user;
"

# Update connection strings to use new user
```

**2. Database Backup**
```bash
# Create backup script
cat > backup_db.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec library_grpc-postgres-1 pg_dump -U postgres library_db > backup_${DATE}.sql
# Upload to cloud storage or remote location
EOF

chmod +x backup_db.sh

# Add to crontab for daily backups
echo "0 2 * * * /path/to/backup_db.sh" | crontab -
```

### Monitoring & Logging

**1. Application Monitoring**
```yaml
# Add to docker-compose.prod.yml
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
```

**2. Log Management**
```bash
# Configure log rotation
sudo tee /etc/logrotate.d/docker-containers << EOF
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    size=1M
    missingok
    delaycompress
    copytruncate
}
EOF
```

### Performance Optimization

**1. Docker Optimization**
```bash
# Optimize Docker daemon
sudo tee /etc/docker/daemon.json << EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2"
}
EOF

sudo systemctl restart docker
```

**2. System Optimization**
```bash
# Increase file limits
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize kernel parameters
echo "net.core.somaxconn = 65536" | sudo tee -a /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 65536" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

## 🔄 Deployment Process

### Step-by-Step Deployment

**1. Prepare Server**
```bash
# Create application directory
sudo mkdir -p /opt/library-system
cd /opt/library-system

# Clone repository
git clone https://github.com/shanushaan/library_grpc.git .

# Set permissions
sudo chown -R $USER:$USER /opt/library-system
```

**2. Configure Environment**
```bash
# Copy production configuration
cp docker-compose.prod.yml docker-compose.yml
cp .env.prod .env

# Update configuration files
nano .env  # Update passwords and secrets
```

**3. Deploy Services**
```bash
# Build and start services
docker-compose build
docker-compose up -d

# Verify deployment
docker-compose ps
docker-compose logs
```

**4. Configure Reverse Proxy**
```bash
# Install and configure Nginx
sudo apt install nginx
sudo cp nginx.conf /etc/nginx/sites-available/library-system
sudo ln -s /etc/nginx/sites-available/library-system /etc/nginx/sites-enabled/
sudo systemctl enable nginx
sudo systemctl start nginx
```

**5. Setup SSL Certificate**
```bash
# Using Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### Health Checks

**1. Service Health**
```bash
# Check all services
docker-compose ps

# Test API endpoints
curl -k https://yourdomain.com/api/
curl -k https://yourdomain.com/

# Check database
docker exec library_grpc-postgres-1 pg_isready -U postgres
```

**2. Performance Testing**
```bash
# Install testing tools
sudo apt install apache2-utils

# Test API performance
ab -n 1000 -c 10 https://yourdomain.com/api/

# Test frontend
ab -n 100 -c 5 https://yourdomain.com/
```

## 🔒 Security Hardening

### System Security

**1. Firewall Configuration**
```bash
# Configure UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

**2. Fail2Ban Setup**
```bash
# Install and configure Fail2Ban
sudo apt install fail2ban

# Configure for Nginx
sudo tee /etc/fail2ban/jail.local << EOF
[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10
EOF

sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### Application Security

**1. Update Default Passwords**
```bash
# Update admin passwords in database
docker exec -it library_grpc-postgres-1 psql -U postgres -d library_db -c "
UPDATE users SET password_hash = 'new_secure_hash' WHERE username = 'admin';
"
```

**2. Enable HTTPS Only**
```javascript
// Update frontend configuration
// In React app, ensure all API calls use HTTPS
const API_BASE_URL = 'https://yourdomain.com/api';
```

## 📊 Maintenance

### Regular Maintenance Tasks

**1. Daily Tasks**
```bash
# Check service status
docker-compose ps

# Check disk usage
df -h
docker system df

# Check logs for errors
docker-compose logs --tail=100 | grep -i error
```

**2. Weekly Tasks**
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Clean Docker resources
docker system prune -f

# Backup database
./backup_db.sh
```

**3. Monthly Tasks**
```bash
# Update Docker images
docker-compose pull
docker-compose up -d

# Review security logs
sudo journalctl -u fail2ban --since "1 month ago"

# Check SSL certificate expiry
sudo certbot certificates
```

### Scaling Considerations

**1. Horizontal Scaling**
```yaml
# Scale API gateway
docker-compose up -d --scale api-gateway-node=3

# Load balancer configuration needed
```

**2. Database Scaling**
```yaml
# Read replicas for PostgreSQL
postgres-replica:
  image: postgres:13
  environment:
    PGUSER: replicator
    POSTGRES_PASSWORD: replica_password
  command: |
    bash -c "
    pg_basebackup -h postgres -D /var/lib/postgresql/data -U replicator -v -P -W
    echo 'standby_mode = on' >> /var/lib/postgresql/data/recovery.conf
    postgres
    "
```

## 🎆 Troubleshooting Production Issues

### Common Production Issues

**1. High Memory Usage**
```bash
# Check memory usage
free -h
docker stats

# Restart services if needed
docker-compose restart
```

**2. Database Connection Issues**
```bash
# Check database connections
docker exec library_grpc-postgres-1 psql -U postgres -c "SELECT * FROM pg_stat_activity;"

# Restart database if needed
docker-compose restart postgres
```

**3. SSL Certificate Issues**
```bash
# Renew certificates
sudo certbot renew

# Test certificate
sudo certbot certificates
```

### Emergency Procedures

**1. Service Recovery**
```bash
# Quick restart
docker-compose restart

# Full recovery
docker-compose down
docker-compose up -d

# Database recovery from backup
docker exec -i library_grpc-postgres-1 psql -U postgres library_db < backup_latest.sql
```

**2. Rollback Procedure**
```bash
# Rollback to previous version
git checkout previous-stable-tag
docker-compose build
docker-compose up -d
```