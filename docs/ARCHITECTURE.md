# CaterOps AI - Architecture & Design Document

## System Architecture

### High-Level Flow

```
User Input
    ↓
[React Frontend]
    ↓ (HTTP POST)
[Express Backend]
    ↓
[Workflow Orchestrator]
    ├→ [AI Engine]
    ├→ [Business Logic]
    ├→ [Database Models]
    └→ [State Management]
    ↓
[PostgreSQL Database]
    ↓ (Results)
[Frontend - Execution Logs + Plan Output]
```

### Component Breakdown

#### Frontend Layer (React + Vite)

**App.jsx** - Main application container
- State management (logs, plan, loading)
- Orchestrates data flow
- Error handling
- Renders three main panels

**Components:**
- `EventForm.jsx` - Input collection
- `ExecutionLog.jsx` - Step-by-step execution display
- `FinalOutput.jsx` - Results visualization

**Services:**
- `api.js` - HTTP client to backend
- Handles all API communication
- Error management

#### Backend Layer (Node.js + Express)

**Server Setup (server.js)**
- Express app initialization
- Middleware configuration (CORS, JSON)
- Route mounting
- Error handling

**Database Layer (db.js)**
- PostgreSQL connection pooling
- Query execution wrapper
- Connection management

**Routes**
- `eventRoutes.js` - Event CRUD operations
- `workflowRoutes.js` - Workflow execution

**Controllers**
- `eventController.js` - Event endpoints
- `workflowController.js` - Workflow endpoints
- HTTP request/response handling

**Services**
- `workflowService.js` - Orchestration logic
- Coordinates all workflow steps
- Manages execution logs
- Returns structured results

- `aiEngine.js` - Decision logic
- Ingredient calculations
- Staff requirements
- Plan optimization
- (Ready for OpenAI integration)

**Models**
- `eventModel.js` - Event CRUD
- `planModel.js` - Plan & logs CRUD
- `resourceModel.js` - Staff & inventory CRUD

#### Data Layer (PostgreSQL)

**Tables:**
- `events` - Event metadata & status
- `staff` - Available staff pool
- `inventory` - Available ingredients
- `plans` - Execution plans (JSONB)
- `event_staff_assignments` - Staff allocations
- `execution_logs` - Workflow step logs

## Workflow Execution Flow (7 Steps)

```
Request: POST /api/workflow/run/:eventId
    ↓
[1] Parse Input
    - Validate event data
    - Convert to schema
    - Output: Parsed event object
    ↓
[2] Calculate Ingredients
    - Scale by guest count
    - Lookup ingredient database
    - Compute costs
    - Output: Ingredient list + total cost
    ↓
[3] Determine Staff Requirements
    - Apply heuristics (1 cook/30 guests, etc.)
    - Calculate staff costs
    - Output: Staff requirements by role
    ↓
[4] Check Inventory
    - Query available inventory
    - Identify shortages
    - Output: Inventory status
    ↓
[5] Allocate Staff
    - Query available staff
    - Match to requirements
    - Create assignments
    - Output: Staff allocation plan
    ↓
[6] Optimize Plan
    - Analyze costs
    - Suggest efficiencies
    - Generate timeline
    - Output: Optimization recommendations
    ↓
[7] Finalize & Store
    - Create execution plan document
    - Save to database
    - Update event status
    - Return final plan
    ↓
Response: { success: true, plan_id, logs, final_plan }
```

## Data Flow

### Event Creation
```
Frontend Form → API POST /events → Create Event DB → Return event_id
```

### Workflow Execution
```
Frontend "Run AI" → API POST /workflow/run/:eventId
    ↓
Backend receives eventId
    ↓
For each of 7 steps:
    ↓
    Execute step logic
        ↓
    Add execution log to DB
        ↓
    Return step result to frontend
    ↓
Return final plan to frontend
```

### State Management

**Frontend State:**
```javascript
{
  isLoading: boolean,
  executionLogs: Array<Log>,
  finalPlan: Object,
  currentEventId: uuid,
  error: string | null
}
```

**Log Entry Structure:**
```javascript
{
  step: string,           // "Parsing input"
  status: string,         // "completed" | "running" | "failed"
  data: any,             // Step-specific result
  timestamp: string      // ISO timestamp
}
```

**Plan Structure:**
```javascript
{
  event: { ... },
  ingredients: { ... },
  staff_requirements: { ... },
  optimization: { ... },
  timestamp: string,
  status: string
}
```

## AI Integration Points

### Current Implementation (Deterministic MVP)
- Rule-based calculations
- Heuristic staff allocation
- Simple scaling algorithms

### Future OpenAI Integration
Each function in `aiEngine.js` can be upgraded:

```javascript
// Current:
const ingredients = calculateIngredientsWithAI(event);

// Future:
async function calculateIngredientsWithAI(event) {
  const prompt = `
    Event: ${event.guest_count} guests, menu: ${event.menu_type}
    Calculate required ingredients as JSON: { items: [ { name, quantity, unit } ] }
  `;
  
  const response = await openai.chat.completions.create({
    model: "gpt-4",
    messages: [
      { role: "system", content: "You are a catering AI..." },
      { role: "user", content: prompt }
    ],
    response_format: { type: "json_object" }
  });
  
  return JSON.parse(response.choices[0].message.content);
}
```

## Database Design

### Schema Relationships
```
events ←→ plans
  ↓
event_staff_assignments
  ↓
staff

events ← execution_logs

inventory (standalone, globally available)
```

### Indexing Strategy
- Primary: id fields (UUID)
- Secondary: event_id (for joins)
- Tertiary: status, dates (for filtering)
- Full-text: names (future enhancement)

### JSON Storage
`plans.plan_data` uses JSONB for flexible schema:
```json
{
  "event": { ... },
  "ingredients": [ ... ],
  "staff_requirements": [ ... ],
  "optimization": { ... },
  "timeline": { ... },
  "risk_factors": [ ... ],
  "contingency_plans": [ ... ]
}
```

## Error Handling

### Backend Error Flow
```
API Request
    ↓
Controller receives request
    ↓
Try: Execute business logic
    ↓
Catch: Format error message
    ↓
Response: { error, message, statusCode }
    ↓
Frontend displays error banner
```

### Error Types
- **Validation Errors** (400) - Invalid input
- **Not Found** (404) - Resource doesn't exist
- **Server Errors** (500) - Unexpected exceptions

## Performance Considerations

### Database Optimization
- Connection pooling (max 20)
- Query indexes on frequently used fields
- VACUUM schedule for cleanup
- Backup strategy

### API Optimization
- Gzip compression
- JSON parsing optimization
- Request size limits
- Rate limiting (future)

### Frontend Optimization
- Component memoization
- Lazy loading state display
- CSS optimization
- Asset bundling (Vite)

## Scalability Path

### Stage 1: MVP (Current)
- Single database instance
- Synchronous workflow execution
- In-memory logs

### Stage 2: Ready for Scale
- Add message queue (Bull/Redis)
- Async job processing
- Webhook support
- Caching layer

### Stage 3: Enterprise
- Multi-region database (read replicas)
- Microservices architecture
- Event streaming (Kafka)
- Advanced analytics

## Security Architecture

### Current (MVP)
- CORS enabled for localhost
- Basic input validation
- Environment variables for secrets

### Production Recommendations
- JWT authentication
- OAuth2 integration
- Rate limiting middleware
- Input sanitization
- SQL injection prevention (using parameterized queries ✓)
- HTTPS enforcement
- CSRF protection
- Request logging

## Testing Strategy

### Unit Tests
- Individual functions in aiEngine.js
- Model query functions
- Controller handlers

### Integration Tests
- API endpoint workflows
- Database transactions
- Error scenarios

### E2E Tests
- Full workflow: event → AI → plan
- UI interaction flows
- Error recovery

## Monitoring & Observability

### Logs
- Backend console output
- Database query logs
- Execution step logs (stored in DB)

### Metrics
- Request latency
- Error rates
- Event completion time
- Resource utilization

### Alerts
- Failed workflow executions
- Database connection issues
- CPU/Memory thresholds

## Technology Rationale

### React + Vite
- ✓ Fast, modern development experience
- ✓ Component-based architecture
- ✓ Hot module replacement

### Express.js
- ✓ Lightweight, flexible
- ✓ Large ecosystem
- ✓ Easy middleware integration

### PostgreSQL
- ✓ ACID compliance
- ✓ JSONB support for flexible schemas
- ✓ Strong query capabilities
- ✓ Reliable, production-ready

### Node.js
- ✓ JavaScript across stack
- ✓ Non-blocking I/O
- ✓ Great for I/O-heavy apps

## Future Enhancements

1. **Real-time Updates**
   - WebSockets for live log streaming
   - Pub/sub for multi-user awareness

2. **Advanced Analytics**
   - Cost prediction
   - Resource optimization ML
   - Historical trend analysis

3. **Integration**
   - Inventory management system
   - Payment gateway
   - Calendar sync

4. **Mobile**
   - React Native app
   - Native iOS/Android

5. **AI Enhancements**
   - GPT-4 integration for complex decisions
   - Machine learning for cost optimization
   - Natural language processing for queries

---

Document Version: 1.0
Last Updated: 2026-04-01
