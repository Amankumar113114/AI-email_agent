# AI Email Agent - Architecture Documentation

## System Overview

The AI Email Agent is a full-stack application that leverages Large Language Models (LLMs) to intelligently manage and process emails. The system consists of a Python-based backend API and a React-based frontend interface.

```
┌─────────────────┐     HTTP/REST      ┌─────────────────┐
│   React Frontend │ ◄────────────────► │  FastAPI Backend│
│   (Vite + React) │                    │   (Python)      │
└─────────────────┘                    └────────┬────────┘
       │                                         │
       │                                         │
       ▼                                         ▼
GitHub Pages                          Groq AI API (LLM)
(Free Hosting)                        (Free Tier)
```

## Backend Architecture

### Core Components

#### 1. EmailAgent (`email_agent.py`)
The main orchestrator class that coordinates all email processing operations.

```python
class EmailAgent:
    - compressor: ContextCompressor      # Thread summarization
    - classifier: SmartClassifier        # Email categorization
    - reply_generator: ReplyGenerator    # AI reply generation
    - threads: Dict[str, EmailThread]    # Thread management
```

**Key Methods:**
- `process_email()` - Full pipeline processing
- `get_or_create_thread()` - Thread management
- `batch_process()` - Multiple email processing

#### 2. ContextCompressor
Compresses email threads into structured context using LLM.

**Process:**
1. Build thread content from email chain
2. Send to LLM with structured prompt
3. Parse JSON response
4. Cache results for performance

**Output:**
```python
CompressedContext:
    - summary: str
    - key_points: List[str]
    - decisions: List[str]
    - action_items: List[Dict]
    - sentiment: str
    - urgency_score: float
```

#### 3. SmartClassifier
Multi-label email classification with priority detection.

**Features:**
- Keyword-based urgency detection
- LLM-powered category classification
- Confidence scoring
- Priority calculation

**Categories:**
- Work, Personal, Finance, Promotions
- Support, Urgent, Meeting, Follow-up

#### 4. ReplyGenerator
Generates context-aware email replies.

**Process:**
1. Analyze email context
2. Extract key points and action items
3. Generate appropriate tone
4. Create professional reply

### Data Models

#### Email
```python
@dataclass
class Email:
    id: str
    subject: str
    sender: str
    sender_name: str
    recipients: List[str]
    body: str
    thread_id: Optional[str]
    timestamp: datetime
    is_read: bool
```

#### EmailThread
```python
@dataclass
class EmailThread:
    thread_id: str
    emails: List[Email]
    subject: str
    participants: List[str]
    last_updated: datetime
```

### API Server (`api_server.py`)

FastAPI-based REST API with the following structure:

```
/api_server.py
├── FastAPI App Setup
├── CORS Configuration
├── Pydantic Models (Request/Response)
├── Helper Functions
├── API Endpoints
└── Demo Data Initialization
```

**Storage:** In-memory dictionaries (replace with database for production)

## Frontend Architecture

### Component Hierarchy

```
App.jsx
├── Sidebar
│   ├── Navigation filters
│   ├── Compose button
│   └── Stats display
├── TopBar
│   ├── SearchBar
│   ├── Refresh button
│   └── ConnectionStatus
├── EmailList
│   └── EmailItem (multiple)
└── EmailDetail
    ├── Email header
    ├── Tabs (Email/Thread/Analysis)
    └── ReplyComposer (modal)
```

### State Management

Uses React hooks for state management:

```javascript
// useEmailAgent.js - Custom hook
const useEmailAgent = () => {
    - emails: Array
    - threads: Object
    - analysis: Object
    - loading: boolean
    - backendAvailable: boolean
    
    // Methods
    - fetchEmails()
    - processEmail()
    - generateReply()
    - sendReply()
    - getThread()
}
```

### Component Communication

```
User Action → Component → useEmailAgent → API Call → Backend
     ↑                                              ↓
     └────────────── State Update ←─────────────────┘
```

## Data Flow

### Email Processing Flow

```
1. User selects email
   ↓
2. Frontend calls processEmail()
   ↓
3. Backend receives email data
   ↓
4. ContextCompressor.summarize()
   - Build thread content
   - Call LLM API
   - Parse structured response
   ↓
5. SmartClassifier.classify()
   - Detect urgency signals
   - Call LLM for category
   - Calculate priority
   ↓
6. ReplyGenerator.generate()
   - Analyze context
   - Generate reply
   ↓
7. Return results to frontend
   ↓
8. Update UI with analysis
```

### AI Integration Flow

```
Backend → LLM API (Groq/OpenAI)
    │
    ├── Thread Summarization
    │   Prompt: "Analyze thread and extract..."
    │   Response: JSON with summary, key_points, etc.
    │
    ├── Email Classification
    │   Prompt: "Classify email into categories..."
    │   Response: JSON with category, priority, confidence
    │
    └── Reply Generation
        Prompt: "Generate professional reply..."
        Response: JSON with content, tone, actions
```

## Security Considerations

### Current Implementation
- CORS configured for specific origins
- API keys stored in environment variables
- No authentication (demo app)

### Production Recommendations
1. Add user authentication (JWT/OAuth)
2. Implement rate limiting
3. Use HTTPS only
4. Store data in encrypted database
5. Add input validation/sanitization
6. Implement audit logging

## Performance Optimizations

### Backend
- **Caching**: Compression results cached by thread ID
- **Lazy Loading**: Analysis computed on-demand
- **Connection Pooling**: Reuse HTTP connections to LLM API

### Frontend
- **Memoization**: useMemo for filtered emails
- **Lazy Loading**: Components loaded as needed
- **Debouncing**: Search input debounced

## Scalability Considerations

### Current Limitations
- In-memory storage (lost on restart)
- Single instance deployment
- No queue system for AI processing

### Scaling Path
1. **Database**: Replace in-memory with PostgreSQL/MongoDB
2. **Caching**: Add Redis for frequently accessed data
3. **Queue**: Implement Celery + Redis for AI tasks
4. **CDN**: Use CloudFlare for static assets
5. **Microservices**: Split AI processing to separate service

## Deployment Architecture

### Production Setup

```
┌─────────────────┐
│   GitHub Pages  │  (Static Frontend)
│   (Free)        │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│   Render.com    │  (Backend API)
│   (Free Tier)   │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│   Groq API      │  (LLM Processing)
│   (Free Tier)   │
└─────────────────┘
```

### CI/CD Pipeline

```
Git Push → GitHub Actions → Build → Deploy
                │
                ├── Frontend → GitHub Pages
                └── Backend → Render (auto)
```

## Monitoring & Debugging

### Logs
- Backend: Render dashboard logs
- Frontend: Browser console

### Health Checks
- Backend root endpoint (`/`)
- Frontend connection status indicator

### Error Handling
- Backend: Try-catch with fallback responses
- Frontend: Error boundaries + fallback UI

## Future Enhancements

### Features
- [ ] Real email provider integration (Gmail/Outlook API)
- [ ] User authentication system
- [ ] Email scheduling
- [ ] Custom AI training
- [ ] Mobile app

### Technical
- [ ] WebSocket for real-time updates
- [ ] Database persistence
- [ ] Multi-tenant support
- [ ] API rate limiting
- [ ] Comprehensive test suite

## Development Guidelines

### Adding New Features

1. **Backend Feature:**
   - Add endpoint in `api_server.py`
   - Implement logic in `email_agent.py`
   - Update models if needed
   - Add tests

2. **Frontend Feature:**
   - Create/update component
   - Add to `useEmailAgent.js` hook
   - Update styles in `App.css`
   - Test responsiveness

### Code Style
- Backend: PEP 8, type hints
- Frontend: ESLint, Prettier
- Commits: Conventional commits

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Groq API Documentation](https://console.groq.com/docs)
- [Render Documentation](https://render.com/docs)
