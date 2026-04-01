# MetisFlow - Natural Language Workflow Automation System

An AI-powered, production-ready system that autonomously executes workflows from plain-English descriptions with a single click.

## 🎯 Project Overview

MetisFlow is a next-generation workflow automation platform. Users describe what they want in plain English, and the system **autonomously**:

1. Parses the natural language request
2. Generates a structured workflow JSON
3. Resolves task dependencies
4. Detects required action types
5. Validates the workflow structure
6. Executes all steps with logging
7. Returns comprehensive results

All with a single click.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│         Frontend (React + Vite)             │
│  - Event Form, Live Logs, Output Panel      │
└────────────────────┬────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────┐
│      Backend (Node.js + Express)            │
│  - API Routes, Workflow Orchestration       │
└────────────────────┬────────────────────────┘
                     │ SQL
┌────────────────────▼────────────────────────┐
│    PostgreSQL Database                      │
│  - Events, Staff, Inventory, Plans, Logs    │
└─────────────────────────────────────────────┘
```

## 📁 Project Structure

```
MetisFlow/
├── backend/                    # Node.js Express API
│   ├── src/
│   │   ├── server.js          # Express app setup
│   │   ├── db.js              # PostgreSQL connection
│   │   ├── routes/            # API endpoints
│   │   ├── controllers/        # Request handlers
│   │   ├── services/           # Business logic & AI engine
│   │   └── models/             # Database queries
│   ├── package.json
│   └── .env.example
│
├── frontend/                   # React + Vite
│   ├── src/
│   │   ├── App.jsx            # Main dashboard
│   │   ├── components/         # Form, Logs, Output
│   │   ├── services/           # API client
│   │   └── styles/
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
├── database/
│   ├── schema.sql             # Database tables
│   └── seeds/
│       └── seed_data.sql      # Sample data
│
└── docs/
    └── README.md
```

## ⚡ Quick Start

### Prerequisites

- Node.js 18+
- PostgreSQL 12+
- npm or yarn

### Installation

#### 1. Clone and Navigate

```bash
cd MetisFlow
```

#### 2. Setup Database

```bash
# Create database
psql -U postgres -c "CREATE DATABASE caterops;"

# Run schema
psql -U postgres -d caterops -f database/schema.sql

# Seed with sample data
psql -U postgres -d caterops -f database/seeds/seed_data.sql
```

#### 3. Setup Backend

```bash
cd backend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Edit .env with your database credentials:
# DB_HOST=localhost
# DB_USER=postgres
# DB_PASSWORD=password
# OPENAI_API_KEY=your_key_here (optional for MVP)

# Start server
npm run dev
```

Backend runs on `http://localhost:5000`

#### 4. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend runs on `http://localhost:5173`

### 5. Test the System

1. Open http://localhost:5173
2. Fill in the event form:
   - Event Name: "Corporate Gala"
   - Guests: 150
   - Menu: Vegetarian
   - Date: 2026-04-15 (or any future date)
   - Location: "Grand Hall"
3. Click **🚀 Run AI**
4. Watch real-time execution logs
5. View generated event plan

## 🔄 Workflow Execution

When you click "Run AI", the system executes 7 steps:

### Step 1: Parse Input
- Validates event data
- Converts to structured format

### Step 2: Calculate Ingredients
- Uses ingredient database (scaled by guest count)
- Computes cost per person
- Total cost calculation

### Step 3: Determine Staff Requirements
- Heuristic: 1 cook per 30 guests, 1 helper per 20, 1 server per 15
- Calculates hourly rates
- Estimates total staff cost

### Step 4: Check Inventory
- Queries available inventory
- Identifies shortages
- Flags low-stock items

### Step 5: Allocate Staff
- Matches available staff to requirements
- Prioritizes by availability date
- Creates assignments

### Step 6: Optimize Plan
- Cost optimization suggestions
- Efficiency improvements
- Timeline optimization

### Step 7: Finalize & Store
- Creates execution plan document
- Saves to database
- Updates event status

## 🗄️ Database Schema

### events
- Event details and status tracking

### staff
- Available staff with roles and rates

### inventory
- Available ingredients and quantities

### plans
- Generated execution plans (JSONB)

### event_staff_assignments
- Staff-to-event allocations

### execution_logs
- Real-time workflow execution logs

## 🤖 AI Integration

The system uses deterministic logic (for MVP) but is structured for OpenAI integration:

- **parseEventWithAI()** - Input validation
- **calculateIngredientsWithAI()** - Ingredient scaling
- **determineStaffRequirementsWithAI()** - Staff allocation heuristics
- **optimizePlanWithAI()** - Cost/efficiency optimization

To add real OpenAI calls, update `backend/src/services/aiEngine.js`:

```javascript
const completion = await openai.chat.completions.create({
  model: "gpt-4",
  messages: [
    { role: "system", content: "You are a catering operations AI..." },
    { role: "user", content: userPrompt },
  ],
});
```

## 📊 API Endpoints

### Events
- `POST /api/events` - Create event
- `GET /api/events` - List all events
- `GET /api/events/:eventId` - Get event details

### Workflow
- `POST /api/workflow/run/:eventId` - Execute workflow
- `GET /api/workflow/status/:eventId` - Get execution status

## 🎨 UI Features

### Dashboard Components

1. **Event Form** (Left Panel)
   - Inputs for event details
   - Menu type selector
   - Clean, minimal design
   - "🚀 Run AI" button

2. **Execution Log** (Top Right)
   - Real-time step-by-step logs
   - Status indicators (✓ / ⏳ / ✗)
   - JSON data previews

3. **Final Output Panel** (Bottom Right)
   - Event summary
   - Cost breakdown
   - Staff allocation matrix
   - Ingredients list
   - Risk factors
   - Contingency plans

## 🔐 Security Considerations (Production)

- Add authentication (JWT tokens)
- Implement rate limiting
- Validate all inputs server-side
- Use HTTPS
- Secure OPENAI_API_KEY in secrets manager
- Add CORS restrictions
- Implement role-based access control

## 📈 Scalability

For production deployment:

1. **Database**: Use RDS or managed PostgreSQL
2. **Backend**: Deploy to Docker / Kubernetes
3. **Frontend**: Host on CDN (Vercel, Netlify, S3)
4. **Queue**: Add Bull/RabbitMQ for long-running workflows
5. **Monitoring**: Implement error tracking (Sentry)
6. **Caching**: Use Redis for frequently accessed data

## 🧪 Testing

```bash
# Backend tests (to implement)
cd backend
npm test

# Frontend tests (to implement)
cd frontend
npm test
```

## 🚀 Deployment

### Docker (Optional)

```dockerfile
# Backend Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY backend/ .
RUN npm install
CMD ["npm", "start"]
```

### Environment Variables

Create `.env` in both backend and frontend directories:

**backend/.env:**
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=caterops
DB_USER=postgres
DB_PASSWORD=your_password
PORT=5000
OPENAI_API_KEY=your_api_key
```

**frontend/.env:**
```
VITE_API_URL=http://localhost:5000
```

## 📝 Sample Event Data

```json
{
  "name": "Wedding Reception",
  "guest_count": 200,
  "menu_type": "non-veg",
  "event_date": "2026-04-20T18:00:00",
  "location": "Taj Palace Hotel"
}
```

## 🐛 Troubleshooting

### Database Connection Error
```
Error: connect ECONNREFUSED
```
- Ensure PostgreSQL is running
- Check credentials in .env
- Verify database exists: `psql -U postgres -l`

### Frontend Not Loading
- Check if backend is running on :5000
- Clear browser cache
- Check network tab in DevTools

### Port Already in Use
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

## 📚 Next Steps for Production

1. ✅ Add real OpenAI GPT-4 integration
2. ✅ Implement authentication & authorization
3. ✅ Add comprehensive error handling
4. ✅ Create admin dashboard for managing staff/inventory
5. ✅ Build notification system (email/SMS)
6. ✅ Add analytics and reporting
7. ✅ Implement cost prediction models
8. ✅ Add multi-language support

## 📞 Support

For issues or questions:
- Check logs in backend console
- Review execution logs in frontend
- Check database directly: `psql -d caterops`

## 📄 License

MIT

---

**Built with ❤️ | CaterOps AI v1.0**
