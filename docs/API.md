# API Documentation

## Base URL
```
http://localhost:5000/api
```

## Endpoints

### Events API

#### Create Event
**POST** `/events`

Request body:
```json
{
  "name": "Corporate Gala",
  "guest_count": 150,
  "menu_type": "veg",
  "event_date": "2026-04-15T18:00:00",
  "location": "Grand Ballroom"
}
```

Response (201):
```json
{
  "success": true,
  "event": {
    "id": "uuid",
    "name": "Corporate Gala",
    "guest_count": 150,
    "menu_type": "veg",
    "event_date": "2026-04-15T18:00:00",
    "location": "Grand Ballroom",
    "status": "pending",
    "created_at": "2026-04-01T10:30:00"
  }
}
```

#### List All Events
**GET** `/events`

Response (200):
```json
[
  {
    "id": "uuid",
    "name": "Corporate Gala",
    "guest_count": 150,
    "status": "pending",
    "created_at": "2026-04-01T10:30:00"
  }
]
```

#### Get Event by ID
**GET** `/events/:eventId`

Response (200):
```json
{
  "id": "uuid",
  "name": "Corporate Gala",
  "guest_count": 150,
  "status": "pending"
}
```

### Workflow API

#### Run Workflow
**POST** `/workflow/run/:eventId`

Request body (optional, can use event data):
```json
{
  "name": "Corporate Gala",
  "guest_count": 150,
  "menu_type": "veg",
  "event_date": "2026-04-15T18:00:00",
  "location": "Grand Ballroom"
}
```

Response (200):
```json
{
  "success": true,
  "event_id": "uuid",
  "plan_id": "uuid",
  "logs": [
    {
      "step": "Parsing input",
      "status": "completed",
      "data": { ... }
    },
    {
      "step": "Calculating ingredients",
      "status": "completed",
      "data": { ... }
    }
  ],
  "final_plan": {
    "event": { ... },
    "ingredients": { ... },
    "staff_requirements": { ... },
    "optimization": { ... }
  }
}
```

#### Get Workflow Status
**GET** `/workflow/status/:eventId`

Response (200):
```json
{
  "event_id": "uuid",
  "event_status": "planning",
  "plan_status": "draft",
  "execution_logs": [
    {
      "step": "Parsing input",
      "status": "completed",
      "message": "Event data parsed successfully",
      "data": JSON,
      "created_at": "2026-04-01T10:30:00"
    }
  ],
  "plan_data": { ... }
}
```

## Response Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Server Error |

## Error Response Format

```json
{
  "error": "Error message",
  "message": "Detailed error message"
}
```

## Example cURL Requests

### Create Event
```bash
curl -X POST http://localhost:5000/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Wedding Reception",
    "guest_count": 200,
    "menu_type": "non-veg",
    "event_date": "2026-04-20T18:00:00",
    "location": "Taj Palace Hotel"
  }'
```

### Run Workflow
```bash
curl -X POST http://localhost:5000/api/workflow/run/EVENT_ID \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Get Status
```bash
curl http://localhost:5000/api/workflow/status/EVENT_ID
```

## Data Models

### Event
- `id` (UUID): Unique identifier
- `name` (string): Event name
- `guest_count` (number): Number of guests
- `menu_type` (string): 'veg' or 'non-veg'
- `event_date` (timestamp): Event date and time
- `location` (string): Event location
- `status` (string): pending, planning, confirmed, completed, cancelled

### Plan
- `id` (UUID): Unique identifier
- `event_id` (UUID): Related event
- `plan_data` (JSONB): Full execution plan
- `status` (string): draft, finalized, executed, cancelled

### Execution Log
- `id` (UUID): Unique identifier
- `event_id` (UUID): Related event
- `step` (string): Step name
- `status` (string): pending, running, completed, failed
- `message` (string): Log message
- `data` (JSONB): Step-specific data

---

Generated for CaterOps AI v1.0
