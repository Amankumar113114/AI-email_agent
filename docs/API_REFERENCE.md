# API Reference Documentation

## Base URL

**Production:** `https://ai-email-agent-ncpe.onrender.com`

**Local:** `http://localhost:8000`

## Authentication

Currently, no authentication is required. For production, implement JWT or API key authentication.

## Content-Type

All requests should use:
```
Content-Type: application/json
```

---

## Endpoints

### 1. Health Check

Check if the API is running.

```http
GET /
```

**Response:**
```json
{
  "message": "AI Email Agent API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

---

### 2. List Emails

Get all emails with optional filtering.

```http
GET /emails?filter_type={filter}
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `filter_type` | string | Optional filter: `unread`, `urgent`, `work`, `personal`, `meetings`, `followup` |

**Response:**
```json
{
  "emails": [
    {
      "id": "email-001",
      "subject": "Project Alpha Launch",
      "sender": "sarah.chen@company.com",
      "sender_name": "Sarah Chen",
      "recipients": ["you@company.com"],
      "body": "Email body content...",
      "thread_id": "thread-001",
      "timestamp": "2026-02-10T09:00:00",
      "is_read": false,
      "category": "Meeting",
      "priority": "high"
    }
  ]
}
```

---

### 3. Get Single Email

Get details of a specific email.

```http
GET /emails/{email_id}
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `email_id` | string | Email unique identifier |

**Response:**
```json
{
  "id": "email-001",
  "subject": "Project Alpha Launch",
  "sender": "sarah.chen@company.com",
  "sender_name": "Sarah Chen",
  "recipients": ["you@company.com"],
  "body": "Email body content...",
  "thread_id": "thread-001",
  "timestamp": "2026-02-10T09:00:00",
  "is_read": false,
  "cc": [],
  "attachments": [],
  "analysis": {
    "classification": { ... },
    "context": { ... }
  }
}
```

**Error Response:**
```json
{
  "detail": "Email not found"
}
```
Status: `404 Not Found`

---

### 4. Process Email

Process an email with AI analysis.

```http
POST /process
```

**Request Body:**
```json
{
  "email": {
    "id": "email-001",
    "subject": "Project Discussion",
    "sender": "john@example.com",
    "sender_name": "John Doe",
    "recipients": ["you@company.com"],
    "body": "Let's discuss the project timeline...",
    "thread_id": "thread-001",
    "timestamp": "2026-02-15T10:00:00",
    "is_read": false
  }
}
```

**Response:**
```json
{
  "success": true,
  "email_id": "email-001",
  "classification": {
    "primary_category": "Work",
    "secondary_categories": ["Meeting"],
    "priority": "high",
    "priority_score": 0.75,
    "confidence": 0.85,
    "reasoning": "Email discusses project timeline and requests meeting"
  },
  "context": {
    "summary": "Discussion about project timeline and scheduling",
    "key_points": ["Timeline concerns", "Meeting request"],
    "decisions": [],
    "action_items": [
      {
        "action": "Schedule meeting",
        "owner": "you",
        "deadline": "this week"
      }
    ],
    "participants": ["john@example.com"],
    "sentiment": "neutral",
    "urgency_score": 0.7
  },
  "reply": {
    "content": "Thank you for reaching out...",
    "tone": "professional",
    "estimated_response_time": "5 minutes",
    "required_actions": [],
    "suggested_attachments": []
  }
}
```

---

### 5. Generate AI Reply

Generate an AI-powered reply for an email.

```http
POST /generate-reply
```

**Request Body:**
```json
{
  "email_id": "email-001",
  "tone": "professional"
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email_id` | string | Yes | ID of email to reply to |
| `tone` | string | No | Reply tone: `professional`, `friendly`, `concise` |

**Response:**
```json
{
  "content": "Thank you for your email regarding the project timeline...",
  "tone": "professional",
  "estimated_response_time": "5-10 minutes",
  "required_actions": ["Schedule meeting"],
  "suggested_attachments": []
}
```

---

### 6. Send Reply

Mark a reply as sent (mock implementation).

```http
POST /send-reply
```

**Request Body:**
```json
{
  "email_id": "email-001",
  "content": "Your reply message here..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Reply sent successfully",
  "email_id": "email-001",
  "sent_at": "2026-02-15T14:30:00"
}
```

---

### 7. Send New Email

Send a new email (mock implementation).

```http
POST /send
```

**Request Body:**
```json
{
  "subject": "Meeting Tomorrow",
  "sender": "you@company.com",
  "recipients": ["colleague@company.com"],
  "body": "Let's meet tomorrow at 2pm...",
  "thread_id": null
}
```

**Response:**
```json
{
  "success": true,
  "message": "Email sent successfully",
  "email_id": "email-006",
  "sent_at": "2026-02-15T14:30:00"
}
```

---

### 8. Get Thread

Get details of an email thread.

```http
GET /threads/{thread_id}
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `thread_id` | string | Thread unique identifier |

**Response:**
```json
{
  "thread_id": "thread-001",
  "subject": "Project Alpha Launch",
  "emails": [
    {
      "id": "email-001",
      "subject": "Project Alpha Launch",
      "sender": "sarah.chen@company.com",
      ...
    },
    {
      "id": "email-002",
      "subject": "Re: Project Alpha Launch",
      "sender": "you@company.com",
      ...
    }
  ],
  "participants": ["sarah.chen@company.com", "you@company.com"],
  "last_updated": "2026-02-15T14:30:00"
}
```

---

### 9. Mark Email as Read

Mark an email as read.

```http
POST /emails/{email_id}/mark-read
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `email_id` | string | Email unique identifier |

**Response:**
```json
{
  "success": true,
  "email_id": "email-001",
  "is_read": true
}
```

---

### 10. Get Statistics

Get email statistics.

```http
GET /stats
```

**Response:**
```json
{
  "total": 5,
  "unread": 2,
  "urgent": 1,
  "processed": 3,
  "categories": {
    "Work": 2,
    "Meeting": 1,
    "Finance": 1,
    "Personal": 1
  }
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message description"
}
```

### Common Status Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `404` | Resource not found |
| `422` | Validation error |
| `500` | Internal server error |

---

## Rate Limits

Currently no rate limiting. For production, implement:
- 100 requests per minute per IP
- 1000 requests per hour per user

## Interactive API Docs

When running locally, access interactive documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Example Usage

### Python

```python
import requests

BASE_URL = "https://ai-email-agent-ncpe.onrender.com"

# Get all emails
response = requests.get(f"{BASE_URL}/emails")
emails = response.json()["emails"]

# Process an email
email_data = {
    "email": {
        "id": "email-new",
        "subject": "Test Email",
        "sender": "test@example.com",
        "recipients": ["you@company.com"],
        "body": "This is a test email..."
    }
}
response = requests.post(f"{BASE_URL}/process", json=email_data)
analysis = response.json()
```

### JavaScript

```javascript
const BASE_URL = 'https://ai-email-agent-ncpe.onrender.com';

// Get all emails
const response = await fetch(`${BASE_URL}/emails`);
const data = await response.json();

// Generate reply
const replyResponse = await fetch(`${BASE_URL}/generate-reply`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email_id: 'email-001', tone: 'professional' })
});
const reply = await replyResponse.json();
```

### cURL

```bash
# Get emails
curl https://ai-email-agent-ncpe.onrender.com/emails

# Process email
curl -X POST https://ai-email-agent-ncpe.onrender.com/process \
  -H "Content-Type: application/json" \
  -d '{"email": {"id": "test", "subject": "Test", "sender": "test@test.com", "recipients": ["you@test.com"], "body": "Test body"}}'

# Generate reply
curl -X POST https://ai-email-agent-ncpe.onrender.com/generate-reply \
  -H "Content-Type: application/json" \
  -d '{"email_id": "email-001"}'
```
