# Getting Started Guide

## 🎯 Quick Start (5 minutes)

### Windows Users
```bash
# 1. Run setup batch file
setup.bat

# 2. Start backend (in new terminal)
cd backend
npm run dev

# 3. Start frontend (in new terminal)
cd frontend
npm run dev

# 4. Open browser
# http://localhost:5173
```

### macOS/Linux Users
```bash
# 1. Run setup script
chmod +x setup.sh
./setup.sh

# 2. Start backend (in new terminal)
cd backend
npm run dev

# 3. Start frontend (in new terminal)
cd frontend
npm run dev

# 4. Open browser
# http://localhost:5173
```

## 📋 Manual Setup (If setup script doesn't work)

### Step 1: Database Setup

**macOS/Linux:**
```bash
# Start PostgreSQL
brew services start postgresql
# or
sudo systemctl start postgresql

# Create database
createdb caterops

# Load schema
psql -d caterops < database/schema.sql

# Load sample data
psql -d caterops < database/seeds/seed_data.sql
```

**Windows:**
1. Start PostgreSQL from pgAdmin or Services
2. Open pgAdmin and create database `caterops`
3. Run SQL scripts:
   - Right-click database → Restore
   - Select `database/schema.sql`
   - Then select `database/seeds/seed_data.sql`

Or use command line (if psql is in PATH):
```cmd
psql -U postgres -d caterops -f database\schema.sql
psql -U postgres -d caterops -f database\seeds\seed_data.sql
```

### Step 2: Backend Setup

```bash
cd backend

# Copy environment file
cp .env.example .env
# OR on Windows: copy .env.example .env

# Install dependencies
npm install

# Verify database connection by starting server
npm run dev
```

**Expected output:**
```
🚀 CaterOps API running on port 5000
```

### Step 3: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Expected output:**
```
VITE v4.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
```

### Step 4: Test the System

1. **Open Frontend**
   - Go to http://localhost:5173

2. **Fill Event Form**
   - Event Name: `Test Wedding`
   - Guests: `200`
   - Menu: `non-veg`
   - Date: `2026-04-15T18:00`
   - Location: `Grand Hotel`

3. **Click "🚀 Run AI"**

4. **Watch Execution**
   - See 7 steps execute in real-time
   - Each step shows its status (✓ = completed)

5. **View Results**
   - Cost breakdown
   - Staff allocation
   - Ingredients list
   - Risk factors

## 🧪 Test with Sample Data

### Using Curl

**Create Event:**
```bash
curl -X POST http://localhost:5000/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Corporate Annual Dinner",
    "guest_count": 250,
    "menu_type": "veg",
    "event_date": "2026-04-20T19:00:00",
    "location": "Marriott Convention Center"
  }'
```

**Response:**
```json
{
  "success": true,
  "event": {
    "id": "c7b3e0e1-2f4a-4d1f-8c5a-9e7d8f2c1a3b",
    "name": "Corporate Annual Dinner",
    "guest_count": 250,
    "menu_type": "veg",
    "event_date": "2026-04-20T19:00:00",
    "location": "Marriott Convention Center",
    "status": "pending",
    "created_at": "2026-04-01T10:30:00Z"
  }
}
```

**Save the event ID and run workflow:**
```bash
# Replace EVENT_ID with actual ID
curl -X POST http://localhost:5000/api/workflow/run/EVENT_ID \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response (truncated):**
```json
{
  "success": true,
  "event_id": "c7b3e0e1-...",
  "plan_id": "f8a2b1c3-...",
  "logs": [
    {
      "step": "Parsing input",
      "status": "completed",
      "data": { "name": "Corporate Annual Dinner", ... }
    },
    {
      "step": "Calculating ingredients",
      "status": "completed",
      "data": { "ingredients": [...], "total_cost": 2480.50 }
    },
    ...
  ],
  "final_plan": { ... }
}
```

## 🔧 Troubleshooting

### Issue: "Cannot connect to database"
```
Error: connect ECONNREFUSED 127.0.0.1:5432
```

**Solution:**
```bash
# Check if PostgreSQL is running
# macOS
brew services list | grep postgres

# Linux
sudo systemctl status postgresql

# Windows
# Check Services.msc or pgAdmin

# If not running, start it
brew services start postgresql
sudo systemctl start postgresql
```

### Issue: "Database does not exist"
```
Error: database "caterops" does not exist
```

**Solution:**
```bash
# Check existing databases
psql -U postgres -l

# Create it
createdb -U postgres caterops

# Load schema
psql -d caterops < database/schema.sql
```

### Issue: "Port 5000 already in use"
```
Error: listen EADDRINUSE :::5000
```

**Solution:**
```bash
# macOS/Linux - Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Windows - Kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Issue: "Port 5173 already in use"
```bash
# Same as above but for port 5173
lsof -ti:5173 | xargs kill -9
```

### Issue: "npm not found"
```
Error: npm: command not found
```

**Solution:**
- Install Node.js from https://nodejs.org (includes npm)
- Verify: `node -v && npm -v`

### Issue: "psql not found" (PostgreSQL not in PATH)
```
Error: psql: command not found
```

**Solution:**
- Add PostgreSQL bin to PATH
- Or use full path: `/usr/local/bin/psql`
- On Windows, use pgAdmin GUI instead

## 📱 First Test Workflow

### Scenario: Wedding Catering
1. Event: 300 guests, non-vegetarian menu
2. Expected workflow:
   - 10 cooks needed (300/30)
   - 15 helpers needed (300/20)
   - 20 servers needed (300/15)
   - ~2500+ ingredients scaled
   - ~₹21,000+ estimated cost

## 📊 Data Verification

### Check Seeded Data
```bash
# Connect to database
psql -d caterops

# View staff
SELECT name, role, hourly_rate FROM staff;

# View inventory
SELECT name, category, quantity_available FROM inventory;

# List any events created
SELECT name, guest_count, status FROM events;
```

## 🔐 Environment Variables

### Backend (.env)
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=caterops
DB_USER=postgres
DB_PASSWORD=password
PORT=5000
NODE_ENV=development
FRONTEND_URL=http://localhost:5173
OPENAI_API_KEY=your_key_here_optional
```

### Frontend (optional)
No .env needed for local development (uses proxy in Vite config)

## 🎓 Next Learning Steps

1. **Explore Backend Code**
   - `backend/src/services/workflowService.js` - Main workflow
   - `backend/src/services/aiEngine.js` - AI/business logic
   - `backend/src/routes/` - API endpoints

2. **Understand Frontend**
   - `frontend/src/App.jsx` - Main component
   - `frontend/src/components/` - Sub-components
   - `frontend/src/services/api.js` - API calls

3. **Database Queries**
   - See `database/test_queries.sql` for useful queries
   - Connect with pgAdmin for visual browsing

4. **API Testing**
   - Use Postman or Insomnia
   - Import curl commands from API.md

5. **Deployment**
   - Read `docs/DEPLOYMENT.md`
   - Docker setup included
   - Heroku/AWS examples provided

## 💡 Tips & Tricks

### Dev Mode with Auto-Reload
```bash
# Backend (uses nodemon)
cd backend
npm run dev

# Frontend (uses Vite HMR)
cd frontend
npm run dev
```

### Watch Database Changes
```bash
# In psql terminal
WATCH SELECT * FROM events;
```

### Debug API Calls
```bash
# In browser console
fetch('http://localhost:5000/api/events')
  .then(r => r.json())
  .then(d => console.log(d))
```

### View Backend Logs
```bash
# Terminal where backend is running - all logs appear there
# Search for "Step" to find workflow steps
```

## 📞 Support & Help

- **API Issues?** Check `docs/API.md`
- **Deployment?** See `docs/DEPLOYMENT.md`
- **Architecture?** Read `docs/ARCHITECTURE.md`
- **Database?** Query with `database/test_queries.sql`

---

**Ready to demo? Follow Quick Start above and you'll be running in 5 minutes! 🚀**
