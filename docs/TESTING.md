# Testing Guide & Sample Data

## 🧪 Manual Testing Checklist

### Pre-Test Setup
- [ ] PostgreSQL running
- [ ] Backend running on :5000
- [ ] Frontend running on :5173
- [ ] No errors in backend console
- [ ] Browser console open for debugging

## 📝 Test Scenarios

### Test 1: Simple Vegetarian Event (50 guests)

**Objective**: Smoke test with minimal data

**Steps**:
1. Open http://localhost:5173
2. Fill form:
   - Name: "Birthday Party"
   - Guests: "50"
   - Menu: "veg"
   - Date: "2026-04-15T15:00"
   - Location: "Home"
3. Click "🚀 Run AI"

**Expected Results**:
- All 7 steps show ✓
- Estimated cost: ~₹420-500
- Staff: 2 cooks, 3 helpers, 4 servers
- ~20 ingredients listed

---

### Test 2: Large Non-Veg Event (500 guests)

**Objective**: Test with large numbers and complex calculations

**Steps**:
1. Fill form:
   - Name: "Annual Conference Dinner"
   - Guests: "500"
   - Menu: "non-veg"
   - Date: "2026-04-20T18:30"
   - Location: "Convention Center"
2. Click "🚀 Run AI"

**Expected Results**:
- All 7 steps execute
- Estimated cost: ~₹8,500+
- Staff: 17+ required
- Risk factor: "Large event - ensure adequate space"
- Contingency: "Have backup staff available"

---

### Test 3: Enterprise Event (1000 guests)

**Objective**: Stress test with very large event

**Steps**:
```json
{
  "name": "Tech Summit Gala",
  "guest_count": 1000,
  "menu_type": "non-veg",
  "event_date": "2026-04-25T19:00:00",
  "location": "International Convention Center"
}
```

**Expected Results**:
- Massive resource requirements displayed
- Multiple risk factors
- Comprehensive contingency plans
- Est. cost: ~₹40,000+

---

## 🔗 API Testing with Curl

### Test Case 1: Create Event
```bash
curl -X POST http://localhost:5000/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Event 1",
    "guest_count": 100,
    "menu_type": "veg",
    "event_date": "2026-04-15T18:00:00",
    "location": "Test Location"
  }'
```

**Expected Response (201)**:
```json
{
  "success": true,
  "event": {
    "id": "UUID-HERE",
    "name": "Test Event 1",
    "guest_count": 100,
    "menu_type": "veg",
    "status": "pending",
    "created_at": "2026-04-01T10:00:00Z"
  }
}
```

### Test Case 2: Get All Events
```bash
curl http://localhost:5000/api/events
```

**Expected Response (200)**:
```json
[
  {
    "id": "UUID-1",
    "name": "Test Event 1",
    "guest_count": 100,
    "status": "pending"
  },
  {
    "id": "UUID-2",
    "name": "Test Event 2",
    "guest_count": 200,
    "status": "planning"
  }
]
```

### Test Case 3: Get Single Event
```bash
curl http://localhost:5000/api/events/UUID-HERE
```

**Expected Response (200)**:
```json
{
  "id": "UUID-HERE",
  "name": "Test Event 1",
  "guest_count": 100,
  "menu_type": "veg",
  "event_date": "2026-04-15T18:00:00Z",
  "location": "Test Location",
  "status": "pending",
  "created_at": "2026-04-01T10:00:00Z"
}
```

### Test Case 4: Run Workflow
```bash
# Save the event ID from previous response, then:
curl -X POST http://localhost:5000/api/workflow/run/{EVENT_ID} \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected Response (200)**:
```json
{
  "success": true,
  "event_id": "{EVENT_ID}",
  "plan_id": "PLAN_UUID",
  "logs": [
    {
      "step": "Parsing input",
      "status": "completed",
      "data": { ... }
    },
    {
      "step": "Calculating ingredients",
      "status": "completed",
      "data": {...}
    },
    ...
  ],
  "final_plan": { ... }
}
```

### Test Case 5: Get Workflow Status
```bash
curl http://localhost:5000/api/workflow/status/{EVENT_ID}
```

**Expected Response (200)**:
```json
{
  "event_id": "{EVENT_ID}",
  "event_status": "planning",
  "plan_status": "draft",
  "execution_logs": [
    {
      "id": "LOG_UUID",
      "event_id": "{EVENT_ID}",
      "step": "Parsing input",
      "status": "completed",
      "message": "Event data parsed successfully",
      "created_at": "2026-04-01T10:00:00Z"
    },
    ...
  ],
  "plan_data": { ... }
}
```

---

## ❌ Error Testing

### Test Case 6: Invalid Guest Count
```bash
curl -X POST http://localhost:5000/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bad Event",
    "guest_count": 0,
    "menu_type": "veg",
    "event_date": "2026-04-15T18:00:00",
    "location": "Location"
  }'
```

**Expected Response (500)**:
```json
{
  "error": "Workflow execution failed",
  "message": "Guest count must be greater than 0"
}
```

### Test Case 7: Missing Required Fields
```bash
curl -X POST http://localhost:5000/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Incomplete Event"
  }'
```

**Expected Response (400)**:
```json
{
  "error": "Missing required fields",
  "required": ["name", "guest_count", "event_date", "location", "menu_type"]
}
```

### Test Case 8: Non-Existent Event
```bash
curl http://localhost:5000/api/events/00000000-0000-0000-0000-000000000000
```

**Expected Response (404)**:
```json
{
  "error": "Event not found"
}
```

---

## 🗄️ Database Verification

### Verify Seeded Data
```bash
psql -d caterops

# Check staff
SELECT name, role, hourly_rate FROM staff ORDER BY role;

# Check inventory
SELECT name, category, quantity_available FROM inventory LIMIT 5;

# Check indexes
SELECT * FROM pg_indexes WHERE schemaname = 'public';
```

### Verify Execution Flow
```bash
-- After running a workflow, check:
SELECT event_id, step, status FROM execution_logs ORDER BY created_at;

-- View staff assignments
SELECT esa.id, s.name, esa.role FROM event_staff_assignments esa 
JOIN staff s ON esa.staff_id = s.id LIMIT 5;
```

---

## 🚀 Performance Testing

### Test Case 9: Concurrent Requests
```bash
# Create 5 events simultaneously
for i in {1..5}; do
  curl -X POST http://localhost:5000/api/events \
    -H "Content-Type: application/json" \
    -d "{
      \"name\": \"Concurrent Event $i\",
      \"guest_count\": $((100 + i * 50)),
      \"menu_type\": \"veg\",
      \"event_date\": \"2026-04-15T18:00:00\",
      \"location\": \"Location $i\"
    }" &
done
wait
```

**Expected**: All requests complete successfully

---

## 📊 Load Testing Scenario

### Simulate Production Load
```bash
# Create 10 events and run workflows in sequence
for i in {1..10}; do
  # Create event
  EVENT_RESPONSE=$(curl -s -X POST http://localhost:5000/api/events \
    -H "Content-Type: application/json" \
    -d "{
      \"name\": \"Load Test Event $i\",
      \"guest_count\": 150,
      \"menu_type\": \"veg\",
      \"event_date\": \"2026-04-15T18:00:00\",
      \"location\": \"Load Test Location\"
    }")
  
  # Extract event ID
  EVENT_ID=$(echo $EVENT_RESPONSE | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
  
  # Run workflow
  curl -s -X POST http://localhost:5000/api/workflow/run/$EVENT_ID \
    -H "Content-Type: application/json" \
    -d '{}'
  
  echo "Processed event $i: $EVENT_ID"
  sleep 1  # Throttle requests
done
```

---

## 🎯 Frontend Testing Checklist

### UI Component Tests
- [ ] Form inputs accept valid data
- [ ] Form validation shows errors
- [ ] "Run AI" button disables during execution
- [ ] Execution log shows all 7 steps
- [ ] Final output displays cost breakdown
- [ ] Staff allocation matrix renders
- [ ] Ingredients list shows multiple items
- [ ] Error banner displays on failure
- [ ] Success state shows checkmarks

### Responsive Design
- [ ] Desktop layout (1400px+) - 2 columns
- [ ] Tablet layout (1024px) - Stacked
- [ ] Mobile layout (768px) - Single column
- [ ] All fonts readable
- [ ] All buttons clickable

### Browser Compatibility
- [ ] Chrome - All features
- [ ] Firefox - All features
- [ ] Safari - All features
- [ ] Edge - All features

---

## 📈 Success Criteria

### MVP Success Metrics
| Metric | Target | Actual |
|--------|--------|--------|
| Events created | 10+ | _ |
| Workflows run | 5+ | _ |
| Error rate | < 5% | _ |
| Execution time | 2-5s | _ |
| All steps complete | 100% | _ |

### Test Coverage
| Component | Target | Status |
|-----------|--------|--------|
| Backend API | 80% | _ |
| Frontend UI | 70% | _ |
| Database | 100% | ✓ |
| Workflow logic | 95% | _ |

---

## 🐛 Known Issues & Workarounds

### Issue: Database connection fails on restart
**Workaround**: Restart PostgreSQL service
```bash
brew services restart postgresql
```

### Issue: Frontend shows "Cannot GET /"
**Workaround**: Ensure backend is running and CORS is enabled

### Issue: Workflow takes >10 seconds
**Workaround**: Check database connections, restart backend

---

## 📝 Test Report Template

```
Test Date: ___________
Tester: ___________
Environment: [Dev/Stage/Prod]
Database: [Fresh/Seeded]

Test Results:
- Test 1 (Simple Event): [PASS/FAIL]
- Test 2 (Large Event): [PASS/FAIL]
- Test 3 (API): [PASS/FAIL]
- Test 4 (Error Handling): [PASS/FAIL]
- Test 5 (Database): [PASS/FAIL]

Issues Found:
1. __________
2. __________

Performance:
- Avg Event Creation: ___ ms
- Avg Workflow Execution: ___ ms
- API Response Time: ___ ms

Sign-off: ___________
```

---

**Testing Version**: 1.0
**Last Updated**: 2026-04-01
