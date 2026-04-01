#!/bin/bash

# CaterOps AI - Quick Setup Script
# Automates database and dependency setup

set -e

echo "🍽️  CaterOps AI - Quick Setup"
echo "=============================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if PostgreSQL is installed
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}PostgreSQL not found. Please install PostgreSQL first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ PostgreSQL found${NC}"

# Create database
echo -e "${BLUE}Creating database...${NC}"
psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'caterops'" | grep -q 1 || \
    psql -U postgres -c "CREATE DATABASE caterops;" || true
echo -e "${GREEN}✓ Database created${NC}"

# Run schema
echo -e "${BLUE}Running database schema...${NC}"
psql -U postgres -d caterops -f database/schema.sql
echo -e "${GREEN}✓ Schema loaded${NC}"

# Seed data
echo -e "${BLUE}Seeding sample data...${NC}"
psql -U postgres -d caterops -f database/seeds/seed_data.sql
echo -e "${GREEN}✓ Sample data loaded${NC}"

# Setup backend
echo -e "${BLUE}Setting up backend...${NC}"
cd backend

if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
fi

npm install
echo -e "${GREEN}✓ Backend dependencies installed${NC}"

cd ..

# Setup frontend
echo -e "${BLUE}Setting up frontend...${NC}"
cd frontend

npm install
echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

cd ..

echo ""
echo -e "${GREEN}=============================="
echo "✓ Setup Complete!"
echo -e "=============================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Backend:  cd backend && npm run dev"
echo "2. Frontend: cd frontend && npm run dev"
echo "3. Open:     http://localhost:5173"
echo ""
echo -e "${YELLOW}Make sure PostgreSQL is running!${NC}"
