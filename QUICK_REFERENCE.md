# 🚀 Quick Reference - Natural Language Workflows

## Access the System

```
Frontend: http://localhost:5174
Backend:  http://localhost:5000
```

---

## Two Ways to Create Workflows

### Method 1: Natural Language (NEW) ✨
1. Click **✨ Natural Language** tab
2. Type your workflow in plain English
3. Click **🤖 Parse Workflow**
4. Review the generated steps
5. Click **▶️ Execute Workflow**
6. Watch logs and see results

### Method 2: Visual Designer 🎨
1. Click **🎨 Workflow Designer** tab
2. Fill form and add workflow nodes
3. Click **🚀 Run AI**
4. See execution results

---

## Natural Language Examples

### Simple API Call
```
"Check API health at https://api.example.com"
```
Generates: HTTP GET request

### Multi-Step Pipeline
```
"Fetch customer data from database, transform to CSV, upload to S3"
```
Generates: 3-step workflow with dependencies

### Team Notification
```
"Run tests and notify team in Slack if they fail"
```
Generates: Execute code → conditional Slack message

### Data Sync
```
"Get data from API, update Google Sheet, send confirmation email"
```
Generates: 3-step workflow with data passing

---

## Supported Workflow Actions

```
→ API Call (http_request)
→ Update Google Sheets (update_spreadsheet)
→ Send Slack Message (send_message)
→ Send Email (send_email)
→ Database Query (database_query)
→ Execute Code (execute_code)
→ Transform Data (transform_data)
→ Trigger Webhook (webhook_trigger)
```

---

## API Endpoints - Postman Examples

### 1. Convert & Execute
```
POST http://localhost:5000/api/chat/workflow
Content-Type: application/json

{
  "user_request": "Update Google Sheet with API data",
  "auto_execute": true,
  "secrets": {
    "SLACK_WEBHOOK_URL": "https://hooks.slack.com/..."
  }
}
```

### 2. Validate Only
```
POST http://localhost:5000/api/chat/validate
{
  "user_request": "Your workflow description"
}
```

### 3. Execute Pre-built Workflow
```
POST http://localhost:5000/api/chat/execute
{
  "workflow": { ...workflow JSON... },
  "secrets": { ...secrets... }
}
```

---

## Workflow Structure

Generated workflows look like:
```json
{
  "workflow_name": "Sync Data",
  "steps": [
    {
      "id": 1,
      "action": "http_request",
      "params": { "method": "GET", "url": "..." },
      "depends_on": []
    },
    {
      "id": 2,
      "action": "update_spreadsheet",
      "params": { "sheet_id": "...", "data": "{{ step_1_response }}" },
      "depends_on": [1]
    }
  ]
}
```

---

## Execution Response

```json
{
  "success": true,
  "workflow_name": "...",
  "total_steps": 2,
  "steps_completed": 2,
  "duration_ms": 1445,
  "results": {
    "1": { "status_code": 200, "data": {...} },
    "2": { "rows_updated": 50 }
  },
  "logs": [
    {
      "step_id": 1,
      "step_name": "http_request",
      "status": "success",
      "duration_ms": 234,
      "output": {...}
    },
    ...
  ]
}
```

---

## Add External Service Secrets

### Slack
```json
{
  "secrets": {
    "SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  }
}
```

### Google Sheets
```json
{
  "secrets": {
    "GOOGLE_SHEETS_API_KEY": "your-api-key",
    "SHEET_ID": "1BxiMVs0XRA5nFMKUVfIz487UUUistLZeIstLZeI8"
  }
}
```

### Database
```json
{
  "secrets": {
    "DATABASE_URL": "postgres://user:pass@localhost/dbname"
  }
}
```

---

## Troubleshooting

| Error | Solution |
|-------|----------|
| "ENOTFOUND api.com" | API URL is invalid or unreachable |
| "Unknown action: xyz" | Use supported actions only |
| "Dependencies not met" | Check depend_on references valid steps |
| "No results" | External services not configured (use secrets) |

---

## Key Features

✅ Parse any natural language request  
✅ Automatic action detection  
✅ Intelligent dependency resolution  
✅ Real-time execution logging  
✅ Multi-step workflow support  
✅ External API integration  
✅ Data passing between steps  
✅ Error handling & retries  
✅ Works without GPT-4 (heuristic fallback)  

---

## Common Workflows Templates

### 1. Data Pipeline
```
"Get data from [SOURCE], process with [SCRIPT], 
 save to [DESTINATION]"
```

### 2. Notification on Event
```
"Run [TEST/CHECK], if [STATUS], send [MESSAGE] 
 to [CHANNEL/EMAIL]"
```

### 3. CRM Sync
```
"Fetch contacts from [API], update [APP], 
 notify team in [SLACK]"
```

### 4. Reporting
```
"Query [DATABASE], generate [REPORT], 
 email to [RECIPIENT]"
```

### 5. Health Check
```
"Check [SERVICE1], [SERVICE2], [SERVICE3], 
 alert if any fail"
```

---

## Performance Tips

1. **Add less complex workflows** - Fewer steps = Faster execution
2. **Use parallel dependencies** - Steps with same dependency run simultaneously
3. **Cache API responses** - Reference previous step output with `{{ step_N_response }}`
4. **Set timeout** - Add timeout_seconds to params if needed

---

## Next Steps

1. **Try Natural Language Tab**
   - Type: "Get data from API and log it"
   - See workflow auto-generate
   - Check execution logs

2. **Add Real Secrets**
   - Get Slack webhook URL
   - Add Google Sheets API key
   - Configure database connection

3. **Build Complex Workflows**
   - Multi-step pipelines
   - Conditional logic
   - Data transformations

4. **Monitor & Optimize**
   - Check execution metrics
   - Improve step performance
   - Handle errors gracefully

---

**Happy automating! 🎉**
