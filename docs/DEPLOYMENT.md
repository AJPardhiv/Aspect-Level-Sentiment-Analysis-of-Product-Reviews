# Deployment Guide

## Prerequisites

- Docker & Docker Compose (optional)
- Node.js 18+
- PostgreSQL 12+
- Environment configured

## Local Development

### Step 1: Database Setup
```bash
# Start PostgreSQL
# On macOS: brew services start postgresql
# On Linux: sudo systemctl start postgresql
# On Windows: Use pgAdmin or SQL Server Management Studio

# Create database
createdb caterops

# Load schema
psql -d caterops -f database/schema.sql

# Seed data
psql -d caterops -f database/seeds/seed_data.sql
```

### Step 2: Backend Setup
```bash
cd backend
cp .env.example .env
npm install
npm run dev
```

### Step 3: Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Step 4: Access Application
- Frontend: http://localhost:5173
- Backend: http://localhost:5000
- API Docs: http://localhost:5000/health

## Docker Deployment

### Build Docker Images

**Backend Dockerfile** (create `backend/Dockerfile`):
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY src ./src
EXPOSE 5000
CMD ["node", "src/server.js"]
```

**Frontend Dockerfile** (create `frontend/Dockerfile`):
```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  db:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: caterops
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/schema.sql:/docker-entrypoint-initdb.d/schema.sql
      - ./database/seeds/seed_data.sql:/docker-entrypoint-initdb.d/seed.sql

  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      DB_HOST: db
      DB_PORT: 5432
      DB_NAME: caterops
      DB_USER: postgres
      DB_PASSWORD: password
      PORT: 5000
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Run with Docker Compose
```bash
docker-compose up -d
```

Services will be available at:
- Frontend: http://localhost:3000
- Backend: http://localhost:5000

## Production Deployment

### On AWS EC2

1. Create Ubuntu instance
2. Install Node.js and PostgreSQL
3. Clone repository
4. Set environment variables
5. Use PM2 for process management:

```bash
npm install -g pm2
pm2 start src/server.js --name "caterops-backend"
pm2 save
pm2 startup
```

### On Heroku

```bash
# Create app
heroku create caterops-app

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev -a caterops-app

# Deploy
git push heroku main

# Run migrations
heroku run psql -f database/schema.sql
```

### On Vercel (Frontend Only)

```bash
npm install -g vercel
cd frontend
vercel
```

## Environment Variables

### Backend (.env)
```
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=caterops
DB_USER=postgres
DB_PASSWORD=secure_password

# Server
PORT=5000
NODE_ENV=production

# API Keys
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# CORS
FRONTEND_URL=https://yourdomain.com
```

### Frontend (.env)
```
VITE_API_URL=https://api.yourdomain.com
```

## Database Migrations

For future schema changes, create migration files:

```sql
-- database/migrations/001_add_new_table.sql
CREATE TABLE new_table (
  id UUID PRIMARY KEY,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Apply migrations:
```bash
psql -d caterops -f database/migrations/001_add_new_table.sql
```

## Monitoring & Logging

### Backend Logs
```bash
# Development
npm run dev

# Production
tail -f /var/log/caterops/backend.log
```

### Database Monitoring
```bash
# Connect to database
psql -d caterops

# Check active connections
SELECT * FROM pg_stat_activity;

# Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables WHERE schemaname != 'pg_catalog' ORDER BY pg_total_relation_size DESC;
```

### Health Check
```bash
curl http://localhost:5000/health
```

## Troubleshooting

### Database Connection Issues
```bash
# Test connection
psql -U postgres -h localhost -d caterops

# Reset password
ALTER USER postgres WITH PASSWORD 'newpassword';
```

### Port Already in Use
```bash
# Kill process
lsof -i :5000
kill -9 <PID>
```

### Disk Space Issues
```bash
# Check disk usage
df -h

# Vacuum database
psql -d caterops -c "VACUUM FULL;"
```

## Backup & Restore

### Backup Database
```bash
pg_dump -U postgres caterops > caterops_backup.sql
```

### Restore Database
```bash
psql -U postgres -d caterops -f caterops_backup.sql
```

## Performance Optimization

### Database Indexes
Already created in schema.sql, but can add more:
```sql
CREATE INDEX idx_events_created_at ON events(created_at);
CREATE INDEX idx_inventory_category ON inventory(category);
```

### Connection Pooling
The backend uses pg Pool with 20 connections by default. Adjust in `backend/src/db.js`:
```javascript
const pool = new Pool({
  max: 50, // Increase for more concurrent connections
});
```

---

For production support, refer to Node.js, PostgreSQL, and Docker documentation.
