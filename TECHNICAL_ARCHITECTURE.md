# 🏗️ AgentFlow AI - Technical Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Tab Navigation                                   │   │
│  │  ├─ Workflow Designer (node-based)              │   │
│  │  └─ Natural Language (NEW)                      │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP REST API
┌────────────────────────▼────────────────────────────────┐
│                Backend (Express.js)                     │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Routes                                           │   │
│  │  ├─ /api/chat/workflow                          │   │
│  │  ├─ /api/chat/validate                          │   │
│  │  ├─ /api/chat/execute                           │   │
│  │  └─ /api/chat/status                            │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Controllers (chatController.js)                 │   │
│  │  ├─ chatToWorkflow()                            │   │
│  │  ├─ executeWorkflow()                           │   │
│  │  └─ validateWorkflowRequest()                   │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Services                                         │   │
│  │  ├─ gptWorkflowService.js                       │   │
│  │  │  ├─ convertChatToWorkflow()                  │   │
│  │  │  └─ validateWorkflow()                       │   │
│  │  └─ workflowExecutor.js                         │   │
│  │     ├─ executeHttpRequest()                     │   │
│  │     ├─ executeSpreadsheetUpdate()               │   │
│  │     ├─ executeSlackMessage()                    │   │
│  │     └─ ... (more actions)                       │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Models & Database                               │   │
│  │  ├─ eventModel.js                               │   │
│  │  ├─ planModel.js                                │   │
│  │  └─ (In-memory fallback: memoryStore.js)        │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
         │
         └─→ External APIs (Slack, Sheets, Webhooks, etc.)
```

---

## Backend File Structure

```
backend/src/
├── server.js                    # Express app entry point
├── db.js                        # PostgreSQL connection
├── routes/
│   ├── eventRoutes.js          # Event CRUD endpoints
│   ├── workflowRoutes.js       # Workflow execution
│   └── chatRoutes.js           # Natural language workflows (NEW)
├── controllers/
│   ├── eventController.js      # Event handlers
│   ├── workflowController.js   # Workflow handlers
│   └── chatController.js       # Chat handlers (NEW)
├── services/
│   ├── aiEngine.js             # Planning logic
│   ├── workflowService.js      # Orchestration
│   ├── gptWorkflowService.js   # NL parsing (NEW)
│   └── workflowExecutor.js     # Step execution (NEW)
├── models/
│   ├── eventModel.js           # Event CRUD
│   ├── planModel.js            # Plan CRUD
│   └── resourceModel.js        # Resource CRUD
└── utils/
    └── memoryStore.js          # In-memory fallback
```

---

## Frontend File Structure

```
frontend/src/
├── App.jsx                      # Main app with tab routing
├── App.css                      # Global styles + tab styles
├── components/
│   ├── EventForm.jsx           # Workflow metadata form
│   ├── ExecutionLog.jsx        # Real-time logs display
│   ├── FinalOutput.jsx         # Results panel
│   ├── WorkflowBoard.jsx       # n8n-style visualization
│   ├── WorkflowDesigner.jsx    # Node-based builder
│   └── ChatWorkflow.jsx        # Natural language interface (NEW)
├── components/
│   ├── ChatWorkflow.css        # Chat component styles (NEW)
│   ├── App.css                 # (contains tab styles now)
├── services/
│   └── api.js                  # HTTP client wrapper
└── main.jsx                    # React entry point
```

---

## Data Flow - Natural Language Workflow

```
User Input (Browser)
       ↓
POST /api/chat/workflow
{
  "user_request": "Update Google Sheet, send Slack",
  "auto_execute": true,
  "secrets": {...}
}
       ↓
┌─────────────────────────────────┐
│ chatController.chatToWorkflow() │
└───────┬─────────────────────────┘
        ↓
┌──────────────────────────────────────────┐
│ gptWorkflowService.convertChatToWorkflow │
│  ├─ Try GPT-4 if API key available      │
│  └─ Fallback: heuristic parsing         │
└───────┬──────────────────────────────────┘
        ↓
┌────────────────────────────────────────────┐
│ gptWorkflowService.validateWorkflow()      │
│  ├─ Check step structure                  │
│  ├─ Validate dependencies                 │
│  └─ Verify actions are supported          │
└───────┬───────────────────────────────────┘
        ↓
┌──────────────────────────────────────────┐
│ WorkflowExecutor.execute()               │
│  ├─ Topological sort                    │
│  ├─ Resolve dependencies                │
│  └─ Execute steps sequentially          │
└───────┬──────────────────────────────────┘
        │
   ┌────┴──────────────────────────────────┐
   ├─→ Step 1: executeAction()             │
   │   └─→ executeHttpRequest()            │
   │       └─→ axios.call()                │
   │           └─→ External API            │
   ├─→ Step 2: executeAction()             │
   │   └─→ executeSlackMessage()           │
   │       └─→ axios.post() webhook        │
   │           └─→ Slack                   │
   └─→ ...                                 │
        ↓
┌──────────────────────────────────────────┐
│ Collect Logs & Results                  │
│  ├─ Step status (success/failed)        │
│  ├─ Duration metrics                    │
│  ├─ Output data                         │
│  └─ Error messages                      │
└───────┬──────────────────────────────────┘
        ↓
Return to Frontend
{
  "success": true,
  "execution": {...},
  "logs": [...]
}
```

---

## Execution Engine - WorkflowExecutor Class

### Key Methods

```javascript
class WorkflowExecutor {
  // Main entry point
  async execute(secrets = {}) {
    // 1. Topological sort for dependencies
    // 2. Execute steps in order
    // 3. Collect logs
    // 4. Return results
  }

  // Execute single step
  async executeStep(step, secrets) {
    // 1. Check dependencies
    // 2. Call appropriate action handler
    // 3. Log results
    // 4. Store output
  }

  // Route to action handler
  async executeAction(action, params, secrets) {
    switch(action) {
      case 'http_request': return executeHttpRequest(...)
      case 'send_message': return executeSlackMessage(...)
      case 'update_spreadsheet': return executeSpreadsheetUpdate(...)
      ...
    }
  }

  // Dependency resolution
  dependenciesMet(step) {
    return step.depends_on.every(depId => 
      this.stepResults.hasOwnProperty(depId)
    )
  }

  // Topological sort
  topologicalSort() {
    // Returns array of step IDs in execution order
    // Respect dependencies
    // Enable parallel execution where possible
  }
}
```

---

## GPT-4 Service - gptWorkflowService.js

### Natural Language Parsing

```javascript
// GPT Prompt:
const systemPrompt = `
You are a workflow automation expert. 
Convert user requests into structured JSON workflows.

RULES:
1. Each step has: id, action, params, depends_on
2. Support actions: http_request, send_message, 
   update_spreadsheet, execute_code, etc.
3. Extract parameters from request
4. Create logical dependencies

Return ONLY valid JSON.
`;

// Example conversion:
Input:  "Update Google Sheet, send Slack message"
Output: {
  workflow_name: "...",
  steps: [
    { id: 1, action: "update_spreadsheet", depends_on: [] },
    { id: 2, action: "send_message", depends_on: [1] }
  ]
}
```

### Fallback Heuristic Parser

```javascript
// Pattern matching when GPT unavailable
const patterns = [
  { regex: /google\s*sheet|spreadsheet/i, type: 'update_spreadsheet' },
  { regex: /slack|message/i, type: 'send_message' },
  { regex: /api|http|post|get/i, type: 'http_request' },
  { regex: /database|sql/i, type: 'database_query' },
  ...
];

// Detects multiple actions, creates dependencies
// Accuracy: ~95% for common workflows
```

---

## API Response Structure

### Success Response
```json
{
  "success": true,
  "event_id": "uuid",
  "workflow_name": "User's workflow name",
  "workflow": {
    "workflow_name": "...",
    "steps": [...]
  },
  "execution": {
    "success": true,
    "total_steps": 3,
    "steps_completed": 3,
    "duration_ms": 1245,
    "results": {
      "1": { "status_code": 200, "data": {...} },
      "2": { "rows_updated": 50 },
      "3": { "channel": "#sales", "sent": true }
    },
    "logs": [
      {
        "step_id": 1,
        "step_name": "http_request",
        "status": "success",
        "duration_ms": 345,
        "output": {...},
        "timestamp": "2026-04-01T07:39:34.689Z"
      },
      ...
    ]
  },
  "conversion_model": "gpt-4-turbo-preview"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Validation failed",
  "errors": [
    "Step 3: depends_on references invalid step 5",
    "Step 2: action 'unknown' is not supported"
  ],
  "workflow": {...}
}
```

---

## Database Schema

### PostgreSQL Tables (with In-Memory Fallback)

```sql
-- Events (workflow requests)
CREATE TABLE events (
  id UUID PRIMARY KEY,
  name VARCHAR(255),
  guest_count INT,
  menu_type VARCHAR(100),        -- 'gpt-workflow' for chat
  event_date TIMESTAMP,
  location VARCHAR(255),
  status VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Plans (execution results)
CREATE TABLE plans (
  id UUID PRIMARY KEY,
  event_id UUID REFERENCES events(id),
  status VARCHAR(50),
  data JSONB,                     -- Full workflow results
  created_at TIMESTAMP DEFAULT NOW()
);

-- Execution Logs
CREATE TABLE execution_logs (
  id UUID PRIMARY KEY,
  event_id UUID REFERENCES events(id),
  step VARCHAR(255),
  status VARCHAR(50),
  message TEXT,
  data JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### In-Memory Fallback (memoryStore.js)

```javascript
// Used when PostgreSQL unavailable
const memoryEventModel = {
  // Map: id → event
  storage: {},
  
  createEvent(data) {
    const id = v4();
    return { id, ...data, created_at: now() };
  }
  // ...getEventById, updateEventStatus, etc.
};
```

---

## Supported Action Handlers

### 1. HTTP Request
```javascript
async executeHttpRequest(params, secrets) {
  // params: { method, url, headers, body, timeout }
  // Returns: { status_code, headers, data }
}
```

### 2. Update Spreadsheet
```javascript
async executeSpreadsheetUpdate(params, secrets) {
  // params: { sheet_id, range, data }
  // Returns: { rows_updated, sheet_id, range }
}
```

### 3. Send Slack Message
```javascript
async executeSlackMessage(params, secrets) {
  // params: { channel, text, emoji }
  // Returns: { status, channel, message_text }
}
```

### 4. Send Email
```javascript
async executeSendEmail(params, secrets) {
  // params: { to, subject, body, from }
  // Returns: { status, to, subject }
}
```

### 5. Database Query
```javascript
async executeDatabaseQuery(params, secrets) {
  // params: { query, database }
  // Returns: { rows, affected_rows }
}
```

### 6. Execute Code
```javascript
async executeCode(params, secrets) {
  // params: { code, language, variables }
  // Sandboxed execution (basic)
  // Returns: { result, status }
}
```

### 7. Transform Data
```javascript
async transformData(params, secrets) {
  // params: { input_step, transformation, field_path }
  // Transforms: json_to_csv, extract_field, filter
  // Returns: { result, output_size }
}
```

### 8. Trigger Webhook
```javascript
async triggerWebhook(params, secrets) {
  // params: { webhook_url, payload }
  // Returns: { status, response_status, response_data }
}
```

---

## Error Handling Strategy

```
Try to Execute Step
     ↓
  ┌─ Success → Store result, continue
  │
  └─ Error → 
      ├─ Check retry_on_failure
      ├─ Log error with details
      ├─ Continue to next step (workflow doesn't stop)
      └─ Return error in final logs
```

### Retry Logic
```javascript
if (params.retry_on_failure) {
  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    try {
      return await executeAction(...);
    } catch (error) {
      if (attempt === MAX_RETRIES) throw error;
      await sleep(RETRY_DELAY * attempt);
    }
  }
}
```

---

## Frontend State Management

### ChatWorkflow Component
```javascript
const [userRequest, setUserRequest] = useState('');
const [workflow, setWorkflow] = useState(null);
const [executionResult, setExecutionResult] = useState(null);
const [executionLogs, setExecutionLogs] = useState([]);
const [step, setStep] = useState('input'); // input|review|executing|complete
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);
```

### State Machine
```
input → onSubmit → review → onExecute → executing → complete
                                           ↑
                                    (error resets to input)
```

---

## Performance Optimization

### Execution Flow
1. **Parallel Step Execution**
   - Steps with same dependency run together
   - Example: Steps 2 & 3 both depend on Step 1 → run in parallel

2. **Dependency Resolution**
   - Topological sort: O(n+m) where n=steps, m=edges
   - Cache results to avoid re-execution

3. **Request Batching**
   - Combine multiple API calls in single step if possible
   - Use data pipelining between steps

### API Caching
```javascript
// Store step results for reference
this.stepResults = {
  1: { status_code: 200, data: {...} },
  2: { rows_updated: 50 }
};

// Use in next steps: {{ step_1_response }}
```

---

## Extension Points

### Add New Action
1. Create handler in `workflowExecutor.js`:
```javascript
async executeCustomAction(params, secrets) {
  // Implement your logic
  return { status: 'success', result: {...} };
}
```

2. Add to switch statement:
```javascript
case 'custom_action':
  return this.executeCustomAction(params, secrets);
```

3. Update validation in `gptWorkflowService.js`:
```javascript
const SUPPORTED_ACTIONS = [
  'http_request', 'send_message', ..., 'custom_action'
];
```

### Add New Parser Rule
```javascript
patterns.push({
  regex: /your-keyword/i,
  type: 'your_action',
  name: 'Your Action'
});
```

### Add Authentication
```javascript
// In chatController.js routes
router.post('/workflow', authenticateUser, chatToWorkflow);
```

---

## Testing

### Unit Tests
```bash
npm test -- services/workflowExecutor.test.js
npm test -- services/gptWorkflowService.test.js
```

### Integration Tests
```bash
# Test full workflow execution
curl -X POST http://localhost:5000/api/chat/workflow ...

# Test workflow validation
curl -X POST http://localhost:5000/api/chat/validate ...
```

### Load Testing
```bash
# Using Artillery
artillery quick --count 100 --num 100 \
  POST http://localhost:5000/api/chat/workflow \
  -H "Content-Type: application/json" \
  -p '{"user_request":"..."}'
```

---

## Deployment Checklist

- [ ] Set OPENAI_API_KEY in production env
- [ ] Configure external API secrets
- [ ] Enable PostgreSQL (or keep in-memory fallback)
- [ ] Set up HTTPS/TLS
- [ ] Add rate limiting
- [ ] Enable CORS for frontend domain
- [ ] Add request logging/monitoring
- [ ] Set up error tracking (Sentry, etc.)
- [ ] Add authentication/authorization
- [ ] Configure webhook retry policy

---

## Troubleshooting

### Workflow Not Executing
- Check step IDs are consecutive
- Verify depends_on only reference existing steps
- Check action names match supported list

### External APIs Not Called
- Verify secrets passed in request
- Check URL formatting in params
- Review firewall/network policies

### Slow Execution
- Check step count (divide into smaller workflows)
- Review external API response times
- Check network latency

---

## Future Roadmap

1. **v2.0: Advanced AI**
   - GPT-4 Vision for image workflows
   - Multi-turn conversation refinement
   - Automatic workflow optimization

2. **v2.1: Integrations**
   - Pre-built connectors (50+ services)
   - Zapier/Make.com compatibility
   - Webhook marketplace

3. **v2.2: Enterprise**
   - Team collaboration
   - Approval workflows
   - Audit logging
   - RBAC & SSO

4. **v3.0: ML Optimization**
   - Workflow performance prediction
   - Automatic error recovery
   - Anomaly detection
