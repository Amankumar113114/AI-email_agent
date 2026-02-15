"""
FastAPI Backend Server for Email Agent
Connects the React frontend to the email agent AI
"""

import os
import json
import uvicorn
from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import asdict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from email_agent import EmailAgent, Email, EmailThread, Category, Priority

# ==============================
# FastAPI App Setup
# ==============================

app = FastAPI(
    title="AI Email Agent API",
    description="Backend API for AI-powered email management",
    version="1.0.0"
)

# Enable CORS for frontend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://*.vercel.app",  # Allow all Vercel deployments
]
# Add custom domain from env if set
if os.getenv("FRONTEND_URL"):
    origins.append(os.getenv("FRONTEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global email agent instance
email_agent = EmailAgent()

# In-memory storage (replace with database in production)
emails_db: Dict[str, Email] = {}
threads_db: Dict[str, EmailThread] = {}
analysis_db: Dict[str, Dict] = {}


# ==============================
# Pydantic Models
# ==============================

class EmailCreate(BaseModel):
    subject: str
    sender: str
    sender_name: Optional[str] = ""
    recipients: List[str]
    body: str
    thread_id: Optional[str] = None


class EmailResponse(BaseModel):
    id: str
    subject: str
    sender: str
    sender_name: str
    recipients: List[str]
    body: str
    thread_id: Optional[str]
    timestamp: Optional[str]
    is_read: bool
    category: Optional[str] = None
    priority: Optional[str] = None


class ProcessEmailRequest(BaseModel):
    email: Dict[str, Any]


class GenerateReplyRequest(BaseModel):
    email_id: str
    tone: Optional[str] = "professional"


class SendReplyRequest(BaseModel):
    email_id: str
    content: str


class ProcessResponse(BaseModel):
    success: bool
    email_id: str
    classification: Dict[str, Any]
    context: Dict[str, Any]
    reply: Dict[str, Any]


# ==============================
# Helper Functions
# ==============================

def email_to_dict(email: Email) -> Dict:
    """Convert Email dataclass to dict"""
    return {
        "id": email.id,
        "subject": email.subject,
        "sender": email.sender,
        "sender_name": email.sender_name,
        "recipients": email.recipients,
        "body": email.body,
        "thread_id": email.thread_id,
        "timestamp": email.timestamp.isoformat() if email.timestamp else None,
        "is_read": email.is_read,
        "cc": email.cc,
        "attachments": email.attachments
    }


def dict_to_email(data: Dict) -> Email:
    """Convert dict to Email dataclass"""
    timestamp = None
    if data.get("timestamp"):
        try:
            timestamp = datetime.fromisoformat(data["timestamp"])
        except:
            timestamp = datetime.now()
    
    return Email(
        id=data["id"],
        subject=data["subject"],
        sender=data["sender"],
        sender_name=data.get("sender_name", ""),
        recipients=data.get("recipients", []),
        body=data["body"],
        thread_id=data.get("thread_id"),
        timestamp=timestamp,
        cc=data.get("cc", []),
        attachments=data.get("attachments", []),
        is_read=data.get("is_read", False)
    )


def init_demo_data():
    """Initialize with demo emails"""
    demo_emails = [
        {
            "id": "email-001",
            "subject": "Project Alpha Launch - Timeline Discussion",
            "sender": "sarah.chen@company.com",
            "sender_name": "Sarah Chen",
            "recipients": ["you@company.com"],
            "body": """Hi team,

I wanted to discuss the timeline for Project Alpha. We're currently scheduled to launch on March 15th, but I'm concerned about the testing phase.

Can we schedule a meeting this week to review the current status? I think we need at least 2 more weeks for proper QA.

Please let me know your availability.

Best,
Sarah""",
            "thread_id": "thread-001",
            "timestamp": datetime(2026, 2, 10, 9, 0).isoformat(),
            "is_read": False
        },
        {
            "id": "email-002",
            "subject": "Invoice #1234 - Payment Due",
            "sender": "billing@vendor.com",
            "sender_name": "Vendor Billing",
            "recipients": ["you@company.com"],
            "body": """Dear Customer,

This is a reminder that Invoice #1234 for $5,000 is due on February 20th, 2026.

Please process the payment at your earliest convenience to avoid late fees.

Thank you for your business.

Regards,
Billing Department""",
            "thread_id": "thread-002",
            "timestamp": datetime(2026, 2, 14, 10, 30).isoformat(),
            "is_read": True
        },
        {
            "id": "email-003",
            "subject": "URGENT: Critical bug in production",
            "sender": "dev-team@company.com",
            "sender_name": "Development Team",
            "recipients": ["you@company.com"],
            "body": """URGENT - Action Required

We've discovered a critical bug in the authentication module that is affecting user logins. This needs immediate attention.

Error: Null pointer exception in AuthHandler.java
Impact: All users unable to login

Please prioritize this fix ASAP.

Thanks""",
            "thread_id": "thread-003",
            "timestamp": datetime(2026, 2, 15, 8, 0).isoformat(),
            "is_read": False
        },
        {
            "id": "email-004",
            "subject": "Weekend plans?",
            "sender": "john.doe@personal.com",
            "sender_name": "John Doe",
            "recipients": ["you@company.com"],
            "body": """Hey!

Are you free this weekend? A few of us are planning to go hiking on Saturday morning. Let me know if you want to join!

Cheers,
John""",
            "thread_id": "thread-004",
            "timestamp": datetime(2026, 2, 14, 18, 0).isoformat(),
            "is_read": True
        },
        {
            "id": "email-005",
            "subject": "Q1 Budget Review Meeting",
            "sender": "finance@company.com",
            "sender_name": "Finance Team",
            "recipients": ["you@company.com", "team@company.com"],
            "body": """Hi everyone,

Please join us for the Q1 Budget Review meeting scheduled for:

Date: February 20th, 2026
Time: 2:00 PM - 3:30 PM
Location: Conference Room A / Zoom

Agenda:
- Q1 spending review
- Budget adjustments
- Q2 projections

Please come prepared with your department's numbers.

Best,
Finance Team""",
            "thread_id": "thread-005",
            "timestamp": datetime(2026, 2, 15, 11, 0).isoformat(),
            "is_read": False
        }
    ]
    
    for email_data in demo_emails:
        email = dict_to_email(email_data)
        emails_db[email.id] = email
        
        # Add to thread
        if email.thread_id:
            thread = email_agent.get_or_create_thread(email.thread_id, email.subject)
            thread.add_email(email)
            threads_db[email.thread_id] = thread


# Initialize demo data
init_demo_data()


# ==============================
# API Endpoints
# ==============================

@app.get("/")
def root():
    return {
        "message": "AI Email Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/emails")
def get_emails(filter_type: Optional[str] = None) -> Dict[str, List[Dict]]:
    """Get all emails with optional filtering"""
    emails = list(emails_db.values())
    
    # Apply filters
    if filter_type:
        if filter_type == "unread":
            emails = [e for e in emails if not e.is_read]
        elif filter_type == "urgent":
            # Get analysis for priority
            emails = [e for e in emails if analysis_db.get(e.id, {}).get("classification", {}).get("priority") in ["critical", "high"]]
        elif filter_type in ["work", "personal", "finance", "promotions", "support", "meeting", "follow-up"]:
            emails = [e for e in emails if analysis_db.get(e.id, {}).get("classification", {}).get("primary_category", "").lower() == filter_type.lower()]
    
    # Sort by timestamp (newest first)
    emails.sort(key=lambda e: e.timestamp or datetime.min, reverse=True)
    
    # Add category/priority from analysis if available
    result = []
    for email in emails:
        email_dict = email_to_dict(email)
        if email.id in analysis_db:
            classification = analysis_db[email.id].get("classification", {})
            email_dict["category"] = classification.get("primary_category", "Other")
            email_dict["priority"] = classification.get("priority", "medium")
        result.append(email_dict)
    
    return {"emails": result}


@app.get("/emails/{email_id}")
def get_email(email_id: str) -> Dict:
    """Get a specific email"""
    if email_id not in emails_db:
        raise HTTPException(status_code=404, detail="Email not found")
    
    email = emails_db[email_id]
    email_dict = email_to_dict(email)
    
    # Add analysis if available
    if email_id in analysis_db:
        email_dict["analysis"] = analysis_db[email_id]
    
    return email_dict


@app.post("/process")
def process_email(request: ProcessEmailRequest) -> Dict:
    """Process an email with AI analysis"""
    email_data = request.email
    
    # Convert to Email object
    if "id" not in email_data:
        email_data["id"] = f"email-{len(emails_db) + 1}"
    
    email = dict_to_email(email_data)
    
    # Store email
    emails_db[email.id] = email
    
    # Get or create thread
    thread = None
    if email.thread_id:
        thread = email_agent.get_or_create_thread(email.thread_id, email.subject)
        thread.add_email(email)
        threads_db[email.thread_id] = thread
    
    # Process with AI
    result = email_agent.process_email(email, thread)
    
    if result.get("success"):
        # Store analysis
        analysis_db[email.id] = result
        
        # Update email with category/priority
        classification = result.get("classification", {})
        
        return {
            "success": True,
            "email_id": email.id,
            "classification": classification,
            "context": result.get("context", {}),
            "reply": result.get("reply", {})
        }
    else:
        raise HTTPException(status_code=500, detail=result.get("error", "Processing failed"))


@app.post("/generate-reply")
def generate_reply(request: GenerateReplyRequest) -> Dict:
    """Generate AI reply for an email"""
    email_id = request.email_id
    
    if email_id not in emails_db:
        raise HTTPException(status_code=404, detail="Email not found")
    
    email = emails_db[email_id]
    
    # Get thread
    thread = None
    if email.thread_id and email.thread_id in threads_db:
        thread = threads_db[email.thread_id]
    
    # Get or create analysis
    if email_id not in analysis_db:
        result = email_agent.process_email(email, thread)
        if result.get("success"):
            analysis_db[email_id] = result
    
    analysis = analysis_db.get(email_id, {})
    
    # Generate reply
    reply_result = email_agent.reply_generator.generate_reply(
        email,
        email_agent.compressor.compress_thread(thread) if thread else email_agent.compressor.compress_thread(EmailThread(thread_id=email.id, emails=[email])),
        email_agent.classifier.classify(
            email,
            email_agent.compressor.compress_thread(thread) if thread else email_agent.compressor.compress_thread(EmailThread(thread_id=email.id, emails=[email]))
        ),
        tone=request.tone
    )
    
    return {
        "content": reply_result.content,
        "tone": reply_result.tone,
        "estimated_response_time": reply_result.estimated_response_time,
        "required_actions": reply_result.required_actions,
        "suggested_attachments": reply_result.suggested_attachments
    }


@app.post("/send-reply")
def send_reply(request: SendReplyRequest) -> Dict:
    """Send a reply (mock implementation)"""
    email_id = request.email_id
    
    if email_id not in emails_db:
        raise HTTPException(status_code=404, detail="Email not found")
    
    # In a real implementation, this would send the email
    # For now, just mark as read and return success
    emails_db[email_id].is_read = True
    
    return {
        "success": True,
        "message": "Reply sent successfully",
        "email_id": email_id,
        "sent_at": datetime.now().isoformat()
    }


@app.post("/send")
def send_email(email_data: EmailCreate) -> Dict:
    """Send a new email (mock implementation)"""
    email_id = f"email-{len(emails_db) + 1}"
    
    email = Email(
        id=email_id,
        subject=email_data.subject,
        sender="you@company.com",
        sender_name="You",
        recipients=email_data.recipients,
        body=email_data.body,
        thread_id=email_data.thread_id,
        timestamp=datetime.now(),
        is_read=True
    )
    
    emails_db[email_id] = email
    
    return {
        "success": True,
        "message": "Email sent successfully",
        "email_id": email_id,
        "sent_at": datetime.now().isoformat()
    }


@app.get("/threads/{thread_id}")
def get_thread(thread_id: str) -> Dict:
    """Get thread details"""
    if thread_id not in threads_db:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    thread = threads_db[thread_id]
    
    return {
        "thread_id": thread_id,
        "subject": thread.subject,
        "emails": [email_to_dict(e) for e in thread.emails],
        "participants": thread.participants,
        "last_updated": thread.last_updated.isoformat() if thread.last_updated else None
    }


@app.post("/emails/{email_id}/mark-read")
def mark_read(email_id: str) -> Dict:
    """Mark an email as read"""
    if email_id not in emails_db:
        raise HTTPException(status_code=404, detail="Email not found")
    
    emails_db[email_id].is_read = True
    
    return {"success": True, "email_id": email_id, "is_read": True}


@app.get("/stats")
def get_stats() -> Dict:
    """Get email statistics"""
    total = len(emails_db)
    unread = sum(1 for e in emails_db.values() if not e.is_read)
    urgent = sum(1 for e in emails_db.values() if analysis_db.get(e.id, {}).get("classification", {}).get("priority") in ["critical", "high"])
    
    categories = {}
    for analysis in analysis_db.values():
        cat = analysis.get("classification", {}).get("primary_category", "Other")
        categories[cat] = categories.get(cat, 0) + 1
    
    return {
        "total": total,
        "unread": unread,
        "urgent": urgent,
        "processed": len(analysis_db),
        "categories": categories
    }


# ==============================
# Run Server
# ==============================

if __name__ == "__main__":
    print("Starting AI Email Agent API Server...")
    print("API Documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
