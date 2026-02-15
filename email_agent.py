"""
AI Email Management Agent
--------------------------
Features:
- Advanced thread compression with context preservation
- Multi-label email categorization with priority scoring
- Context-aware smart reply generation
- Email threading and conversation management
- Batch processing capabilities
"""

import os
import re
import json
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from dotenv import load_dotenv

# ==============================
# Configuration
# ==============================

load_dotenv()

# Provider selection: "openai" or "ollama"
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower()
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini" if AI_PROVIDER == "openai" else "llama3.2")

client = None

if AI_PROVIDER == "openai":
    from openai import OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in environment variables.")
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    # Ollama local setup
    import requests
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    print(f"Using Ollama at {OLLAMA_BASE_URL} with model: {MODEL_NAME}")


# ==============================
# Enums and Constants
# ==============================

class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Category(Enum):
    WORK = "Work"
    PERSONAL = "Personal"
    FINANCE = "Finance"
    PROMOTIONS = "Promotions"
    SUPPORT = "Support"
    URGENT = "Urgent"
    MEETING = "Meeting"
    FOLLOW_UP = "Follow-up"
    OTHER = "Other"


# ==============================
# Data Models
# ==============================

@dataclass
class Email:
    id: str
    subject: str
    sender: str
    sender_name: str = ""
    recipients: List[str] = field(default_factory=list)
    cc: List[str] = field(default_factory=list)
    body: str = ""
    thread_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    attachments: List[str] = field(default_factory=list)
    is_read: bool = False

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class CompressedContext:
    """Compressed representation of email thread context"""
    summary: str
    key_points: List[str]
    decisions: List[str]
    action_items: List[Dict[str, str]]
    participants: List[str]
    sentiment: str
    urgency_score: float


@dataclass
class ClassificationResult:
    """Multi-label classification with priority"""
    primary_category: Category
    secondary_categories: List[Category]
    priority: Priority
    priority_score: float
    confidence: float
    reasoning: str


@dataclass
class ReplySuggestion:
    """Generated reply with metadata"""
    content: str
    tone: str
    estimated_response_time: str
    required_actions: List[str]
    suggested_attachments: List[str]


@dataclass
class EmailThread:
    thread_id: str
    emails: List[Email] = field(default_factory=list)
    subject: str = ""
    participants: List[str] = field(default_factory=list)
    last_updated: Optional[datetime] = None

    def add_email(self, email: Email):
        self.emails.append(email)
        self.emails.sort(key=lambda e: e.timestamp or datetime.min)
        self.last_updated = datetime.now()
        if not self.subject and email.subject:
            self.subject = email.subject
        for p in [email.sender] + email.recipients:
            if p not in self.participants:
                self.participants.append(p)


# ==============================
# Context Compressor
# ==============================

class ContextCompressor:
    """Compresses email threads into structured context"""

    MAX_EMAILS_BEFORE_COMPRESSION = 5
    COMPRESSION_THRESHOLD = 3000

    def __init__(self):
        self.compression_cache: Dict[str, CompressedContext] = {}

    def _estimate_tokens(self, text: str) -> int:
        """Rough estimation of token count"""
        return len(text) // 4

    def _extract_key_info(self, email: Email) -> str:
        """Extract essential information from an email"""
        body_preview = email.body[:500] if len(email.body) > 500 else email.body
        return f"[{email.sender}]: {body_preview}"

    def compress_thread(self, thread: EmailThread, force_refresh: bool = False) -> CompressedContext:
        """Compress a thread into structured context"""
        cache_key = f"{thread.thread_id}_{len(thread.emails)}"

        if not force_refresh and cache_key in self.compression_cache:
            return self.compression_cache[cache_key]

        if len(thread.emails) == 0:
            return CompressedContext(
                summary="Empty thread",
                key_points=[],
                decisions=[],
                action_items=[],
                participants=[],
                sentiment="neutral",
                urgency_score=0.0
            )

        thread_content = self._build_thread_content(thread)

        prompt = f"""Analyze this email thread and extract structured information.

THREAD CONTENT:
{thread_content}

Respond in this exact JSON format:
{{
    "summary": "2-3 sentence overview of the entire conversation",
    "key_points": ["point 1", "point 2", "point 3"],
    "decisions": ["decision 1", "decision 2"],
    "action_items": [
        {{"action": "what needs to be done", "owner": "who should do it", "deadline": "when or null"}}
    ],
    "participants": ["person1", "person2"],
    "sentiment": "positive|negative|neutral|urgent",
    "urgency_score": 0.0-1.0
}}"""

        try:
            if AI_PROVIDER == "openai":
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                result = json.loads(response.choices[0].message.content)
            else:
                # Ollama API
                response = requests.post(
                    f"{OLLAMA_BASE_URL}/api/generate",
                    json={
                        "model": MODEL_NAME,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    }
                )
                response.raise_for_status()
                result = json.loads(response.json()["response"])

            compressed = CompressedContext(
                summary=result.get("summary", ""),
                key_points=result.get("key_points", []),
                decisions=result.get("decisions", []),
                action_items=result.get("action_items", []),
                participants=result.get("participants", []),
                sentiment=result.get("sentiment", "neutral"),
                urgency_score=result.get("urgency_score", 0.0)
            )

            self.compression_cache[cache_key] = compressed
            return compressed

        except Exception as e:
            return self._fallback_compression(thread, str(e))

    def _build_thread_content(self, thread: EmailThread) -> str:
        """Build thread content for compression"""
        parts = []
        for i, email in enumerate(thread.emails, 1):
            parts.append(f"--- Email {i} ---")
            parts.append(f"From: {email.sender}")
            parts.append(f"Subject: {email.subject}")
            parts.append(f"Date: {email.timestamp.strftime('%Y-%m-%d %H:%M') if email.timestamp else 'Unknown'}")
            parts.append(f"Body: {email.body}")
            parts.append("")
        return "\n".join(parts)

    def _fallback_compression(self, thread: EmailThread, error: str) -> CompressedContext:
        """Fallback compression when AI fails"""
        return CompressedContext(
            summary=f"Thread with {len(thread.emails)} emails. Error in compression: {error}",
            key_points=[],
            decisions=[],
            action_items=[],
            participants=list(set(e.sender for e in thread.emails)),
            sentiment="unknown",
            urgency_score=0.5
        )

    def incremental_update(self, thread: EmailThread, new_email: Email) -> CompressedContext:
        """Efficiently update compression with new email"""
        return self.compress_thread(thread, force_refresh=True)


# ==============================
# Smart Classifier
# ==============================

class SmartClassifier:
    """Multi-label email classification with priority detection"""

    URGENT_KEYWORDS = [
        "urgent", "asap", "immediately", "deadline", "emergency",
        "critical", "action required", "please respond", "by eod",
        "by end of day", "by tomorrow", "expired", "overdue"
    ]

    def __init__(self):
        self.category_patterns = {
            Category.MEETING: [r"\b(meeting|calendar|schedule|zoom|teams|call)\b"],
            Category.FINANCE: [r"\b(invoice|payment|bill|receipt|transaction|budget|expense)\b"],
            Category.PROMOTIONS: [r"\b(offer|discount|sale|deal|promo|coupon|limited time)\b"],
            Category.SUPPORT: [r"\b(support|help|ticket|issue|problem|bug|error)\b"],
        }

    def _detect_urgency_signals(self, email: Email, context: CompressedContext) -> Tuple[float, str]:
        """Detect urgency signals in email"""
        text = f"{email.subject} {email.body}".lower()
        score = 0.0
        signals = []

        for keyword in self.URGENT_KEYWORDS:
            if keyword in text:
                score += 0.2
                signals.append(keyword)

        if context.urgency_score > 0.7:
            score += 0.3
            signals.append("high_thread_urgency")

        if any(word in email.subject.lower() for word in ["urgent", "important", "action required"]):
            score += 0.25
            signals.append("urgent_subject")

        return min(score, 1.0), ", ".join(signals)

    def classify(self, email: Email, context: CompressedContext) -> ClassificationResult:
        """Classify email with multi-label support"""

        prompt = f"""Classify this email into categories and determine priority.

EMAIL:
Subject: {email.subject}
From: {email.sender}
Body: {email.body[:1000]}

THREAD CONTEXT:
Summary: {context.summary}
Sentiment: {context.sentiment}

Categories: Work, Personal, Finance, Promotions, Support, Urgent, Meeting, Follow-up, Other

Respond in this exact JSON format:
{{
    "primary_category": "category name",
    "secondary_categories": ["category1", "category2"],
    "priority": "critical|high|medium|low",
    "priority_score": 0.0-1.0,
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}"""

        try:
            if AI_PROVIDER == "openai":
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                result = json.loads(response.choices[0].message.content)
            else:
                response = requests.post(
                    f"{OLLAMA_BASE_URL}/api/generate",
                    json={
                        "model": MODEL_NAME,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    }
                )
                response.raise_for_status()
                result = json.loads(response.json()["response"])

            primary = self._parse_category(result.get("primary_category", "Other"))
            secondary = [self._parse_category(c) for c in result.get("secondary_categories", [])]

            urgency_score, urgency_signals = self._detect_urgency_signals(email, context)

            ai_priority_score = result.get("priority_score", 0.5)
            combined_score = (ai_priority_score + urgency_score) / 2

            final_priority = self._score_to_priority(combined_score)

            return ClassificationResult(
                primary_category=primary,
                secondary_categories=[s for s in secondary if s != primary],
                priority=final_priority,
                priority_score=combined_score,
                confidence=result.get("confidence", 0.8),
                reasoning=f"{result.get('reasoning', '')}. Urgency signals: {urgency_signals}"
            )

        except Exception as e:
            return self._fallback_classification(email, context, str(e))

    def _parse_category(self, name: str) -> Category:
        """Parse category name to enum"""
        name_map = {
            "work": Category.WORK,
            "personal": Category.PERSONAL,
            "finance": Category.FINANCE,
            "promotions": Category.PROMOTIONS,
            "support": Category.SUPPORT,
            "urgent": Category.URGENT,
            "meeting": Category.MEETING,
            "follow-up": Category.FOLLOW_UP,
            "follow_up": Category.FOLLOW_UP,
            "other": Category.OTHER
        }
        return name_map.get(name.lower().replace(" ", "_").replace("-", "_"), Category.OTHER)

    def _score_to_priority(self, score: float) -> Priority:
        """Convert score to priority level"""
        if score >= 0.8:
            return Priority.CRITICAL
        elif score >= 0.6:
            return Priority.HIGH
        elif score >= 0.3:
            return Priority.MEDIUM
        return Priority.LOW

    def _fallback_classification(self, email: Email, context: CompressedContext, error: str) -> ClassificationResult:
        """Fallback classification"""
        text = f"{email.subject} {email.body}".lower()

        if any(k in text for k in ["urgent", "asap", "emergency"]):
            priority = Priority.HIGH
        elif context.urgency_score > 0.6:
            priority = Priority.HIGH
        else:
            priority = Priority.MEDIUM

        return ClassificationResult(
            primary_category=Category.OTHER,
            secondary_categories=[],
            priority=priority,
            priority_score=0.5,
            confidence=0.5,
            reasoning=f"Fallback classification due to error: {error}"
        )


# ==============================
# Reply Generator
# ==============================

class ReplyGenerator:
    """Context-aware reply generation"""

    TONES = {
        "professional": "Formal, respectful, clear",
        "friendly": "Warm, approachable, conversational",
        "concise": "Brief, to-the-point, efficient",
        "detailed": "Comprehensive, thorough, explanatory"
    }

    def generate_reply(
        self,
        email: Email,
        context: CompressedContext,
        classification: ClassificationResult,
        tone: str = "professional"
    ) -> ReplySuggestion:
        """Generate context-aware reply"""

        tone_description = self.TONES.get(tone, self.TONES["professional"])

        prompt = f"""Generate a professional email reply based on context.

ORIGINAL EMAIL:
Subject: {email.subject}
From: {email.sender}
Body: {email.body}

THREAD CONTEXT:
Summary: {context.summary}
Key Points: {', '.join(context.key_points)}
Decisions: {', '.join(context.decisions)}
Action Items: {json.dumps(context.action_items)}
Sentiment: {context.sentiment}

CLASSIFICATION:
Category: {classification.primary_category.value}
Priority: {classification.priority.value}
Reasoning: {classification.reasoning}

TONE: {tone_description}

Generate a reply that:
1. Acknowledges the email appropriately
2. Addresses key points and action items
3. Matches the requested tone
4. Is concise but complete
5. Includes clear next steps if needed

Respond in this exact JSON format:
{{
    "content": "the reply text",
    "tone": "detected tone",
    "estimated_response_time": "how long to respond",
    "required_actions": ["action1", "action2"],
    "suggested_attachments": ["attachment1", "attachment2"]
}}"""

        try:
            if AI_PROVIDER == "openai":
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.4,
                    response_format={"type": "json_object"}
                )
                result = json.loads(response.choices[0].message.content)
            else:
                response = requests.post(
                    f"{OLLAMA_BASE_URL}/api/generate",
                    json={
                        "model": MODEL_NAME,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    }
                )
                response.raise_for_status()
                result = json.loads(response.json()["response"])

            return ReplySuggestion(
                content=result.get("content", ""),
                tone=result.get("tone", tone),
                estimated_response_time=result.get("estimated_response_time", "5-10 minutes"),
                required_actions=result.get("required_actions", []),
                suggested_attachments=result.get("suggested_attachments", [])
            )

        except Exception as e:
            return self._fallback_reply(email, context, str(e))

    def _fallback_reply(self, email: Email, context: CompressedContext, error: str) -> ReplySuggestion:
        """Fallback reply generation"""
        return ReplySuggestion(
            content=f"Thank you for your email regarding '{email.subject}'. I will review and respond shortly.",
            tone="professional",
            estimated_response_time="unknown",
            required_actions=["manual review required"],
            suggested_attachments=[]
        )

    def generate_follow_up_reminder(self, context: CompressedContext) -> str:
        """Generate follow-up reminder based on action items"""
        if not context.action_items:
            return ""

        actions = "\n".join([f"- {item.get('action', 'Unknown action')}" for item in context.action_items])
        return f"Follow-up required:\n{actions}"


# ==============================
# Email Agent
# ==============================

class EmailAgent:
    """Main email management agent"""

    def __init__(self):
        self.compressor = ContextCompressor()
        self.classifier = SmartClassifier()
        self.reply_generator = ReplyGenerator()
        self.threads: Dict[str, EmailThread] = {}

    def get_or_create_thread(self, thread_id: str, subject: str = "") -> EmailThread:
        """Get existing thread or create new one"""
        if thread_id not in self.threads:
            self.threads[thread_id] = EmailThread(thread_id=thread_id, subject=subject)
        return self.threads[thread_id]

    def process_email(
        self,
        email: Email,
        thread: Optional[EmailThread] = None,
        tone: str = "professional"
    ) -> Dict:
        """Process email with full pipeline"""
        try:
            if thread is None:
                thread = self.get_or_create_thread(
                    email.thread_id or email.id,
                    email.subject
                )

            thread.add_email(email)

            compressed_context = self.compressor.compress_thread(thread)

            classification = self.classifier.classify(email, compressed_context)

            reply = self.reply_generator.generate_reply(
                email, compressed_context, classification, tone
            )

            follow_up = self.reply_generator.generate_follow_up_reminder(compressed_context)

            return {
                "success": True,
                "email_id": email.id,
                "thread_id": thread.thread_id,
                "context": {
                    "summary": compressed_context.summary,
                    "key_points": compressed_context.key_points,
                    "decisions": compressed_context.decisions,
                    "action_items": compressed_context.action_items,
                    "participants": compressed_context.participants,
                    "sentiment": compressed_context.sentiment,
                    "urgency_score": compressed_context.urgency_score
                },
                "classification": {
                    "primary_category": classification.primary_category.value,
                    "secondary_categories": [c.value for c in classification.secondary_categories],
                    "priority": classification.priority.value,
                    "priority_score": classification.priority_score,
                    "confidence": classification.confidence,
                    "reasoning": classification.reasoning
                },
                "reply": {
                    "content": reply.content,
                    "tone": reply.tone,
                    "estimated_response_time": reply.estimated_response_time,
                    "required_actions": reply.required_actions,
                    "suggested_attachments": reply.suggested_attachments
                },
                "follow_up_reminder": follow_up,
                "processing_metadata": {
                    "emails_in_thread": len(thread.emails),
                    "thread_subject": thread.subject,
                    "processed_at": datetime.now().isoformat()
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "email_id": email.id
            }

    def batch_process(
        self,
        emails: List[Email],
        tone: str = "professional"
    ) -> List[Dict]:
        """Process multiple emails efficiently"""
        results = []
        for email in emails:
            result = self.process_email(email, tone=tone)
            results.append(result)
        return results

    def get_thread_summary(self, thread_id: str) -> Optional[Dict]:
        """Get summary of a thread"""
        if thread_id not in self.threads:
            return None

        thread = self.threads[thread_id]
        context = self.compressor.compress_thread(thread)

        return {
            "thread_id": thread_id,
            "subject": thread.subject,
            "email_count": len(thread.emails),
            "participants": thread.participants,
            "summary": context.summary,
            "action_items": context.action_items,
            "last_updated": thread.last_updated.isoformat() if thread.last_updated else None
        }


# ==============================
# Example Usage
# ==============================

if __name__ == "__main__":
    agent = EmailAgent()

    thread1 = agent.get_or_create_thread("thread-001", "Project Alpha Launch")

    email1 = Email(
        id="email-001",
        subject="Project Alpha Launch - Timeline Discussion",
        sender="sarah.chen@company.com",
        sender_name="Sarah Chen",
        recipients=["you@company.com"],
        body="""Hi team,

I wanted to discuss the timeline for Project Alpha. We're currently scheduled to launch on March 15th, but I'm concerned about the testing phase.

Can we schedule a meeting this week to review the current status? I think we need at least 2 more weeks for proper QA.

Please let me know your availability.

Best,
Sarah""",
        thread_id="thread-001",
        timestamp=datetime(2026, 2, 10, 9, 0)
    )

    result1 = agent.process_email(email1, thread1, tone="professional")

    print("=" * 60)
    print("EMAIL 1 PROCESSING RESULT")
    print("=" * 60)
    print(f"\n📧 Category: {result1['classification']['primary_category']}")
    print(f"🎯 Priority: {result1['classification']['priority']} ({result1['classification']['priority_score']:.2f})")
    print(f"\n📝 Thread Summary:\n{result1['context']['summary']}")
    print(f"\n🔑 Key Points:")
    for point in result1['context']['key_points']:
        print(f"   • {point}")
    print(f"\n✉️ Suggested Reply:\n{result1['reply']['content']}")

    email2 = Email(
        id="email-002",
        subject="Re: Project Alpha Launch - Timeline Discussion",
        sender="you@company.com",
        sender_name="You",
        recipients=["sarah.chen@company.com"],
        body="""Hi Sarah,

Thanks for flagging this. I agree we should review the timeline.

I'm available Tuesday at 2pm or Wednesday morning. Would either work for you?

Best regards""",
        thread_id="thread-001",
        timestamp=datetime(2026, 2, 10, 14, 30)
    )

    email3 = Email(
        id="email-003",
        subject="Re: Project Alpha Launch - Timeline Discussion",
        sender="sarah.chen@company.com",
        sender_name="Sarah Chen",
        recipients=["you@company.com"],
        body="""Wednesday morning works great. Let's say 10am?

Also, I just found a critical bug in the authentication module that needs immediate attention. Can you prioritize this before our meeting?

Thanks!""",
        thread_id="thread-001",
        timestamp=datetime(2026, 2, 11, 8, 15)
    )

    print("\n" + "=" * 60)
    print("EMAIL 3 PROCESSING (with thread context)")
    print("=" * 60)

    result3 = agent.process_email(email3, thread1, tone="professional")

    print(f"\n📧 Category: {result3['classification']['primary_category']}")
    print(f"🎯 Priority: {result3['classification']['priority']} ({result3['classification']['priority_score']:.2f})")
    print(f"\n📝 Updated Thread Summary:\n{result3['context']['summary']}")
    print(f"\n⚡ Action Items:")
    for item in result3['context']['action_items']:
        print(f"   • {item.get('action')} (Owner: {item.get('owner', 'TBD')})")
    print(f"\n✉️ Suggested Reply:\n{result3['reply']['content']}")

    print("\n" + "=" * 60)
    print("THREAD SUMMARY")
    print("=" * 60)
    summary = agent.get_thread_summary("thread-001")
    print(f"Thread: {summary['subject']}")
    print(f"Emails: {summary['email_count']}")
    print(f"Participants: {', '.join(summary['participants'])}")
