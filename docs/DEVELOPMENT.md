# Development Guide

## Prerequisites

- **Python** 3.11 or higher
- **Node.js** 18 or higher
- **npm** or **yarn**
- **Git**
- **Groq API Key** (free at https://console.groq.com/)

## Project Setup

### 1. Clone Repository

```bash
git clone https://github.com/Amankumar113114/AI-email_agent.git
cd AI-email_agent
```

### 2. Backend Setup

#### Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Configure Environment

Create `.env` file in project root:

```env
AI_PROVIDER=groq
MODEL_NAME=llama3-8b-8192
GROQ_API_KEY=your_groq_api_key_here
```

Get your free Groq API key: https://console.groq.com/

#### Run Backend

```bash
python api_server.py
```

Backend runs at: http://localhost:8000

API docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. Frontend Setup

#### Install Dependencies

```bash
cd frontend
npm install
```

#### Configure Environment

Create `.env` file in `frontend/` directory:

```env
VITE_API_URL=http://localhost:8000
```

#### Run Development Server

```bash
npm run dev
```

Frontend runs at: http://localhost:5173

## Development Workflow

### Running Both Services

**Terminal 1 - Backend:**
```bash
.venv\Scripts\activate  # or source .venv/bin/activate
python api_server.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Making Changes

#### Backend Changes

1. Edit files in project root (`.py` files)
2. Backend auto-reloads on save (if using uvicorn with reload)
3. Test changes at http://localhost:8000/docs

#### Frontend Changes

1. Edit files in `frontend/src/`
2. Vite auto-reloads on save
3. Changes appear immediately at http://localhost:5173

### Code Style

#### Python (Backend)

Follow PEP 8 guidelines:

```bash
# Install formatter
pip install black

# Format code
black .
```

#### JavaScript/React (Frontend)

```bash
# Lint code
npm run lint

# Format code
npm run format
```

## Project Structure Explained

```
AI-email_agent/
├── 📄 api_server.py          # FastAPI application entry point
├── 📄 email_agent.py         # Core AI logic and email processing
├── 📄 requirements.txt       # Python dependencies
├── 📄 render.yaml           # Render deployment configuration
├── 📄 .env                  # Environment variables (not in git)
├── 📄 .env.example          # Example environment file
├── 📁 frontend/             # React application
│   ├── 📁 src/
│   │   ├── 📁 components/   # React UI components
│   │   │   ├── EmailList.jsx      # Email list display
│   │   │   ├── EmailDetail.jsx    # Email detail view
│   │   │   ├── ComposeEmail.jsx   # New email composer
│   │   │   ├── Sidebar.jsx        # Navigation sidebar
│   │   │   ├── SearchBar.jsx      # Search functionality
│   │   │   └── ConnectionStatus.jsx # Backend status
│   │   ├── 📁 hooks/
│   │   │   └── useEmailAgent.js   # API integration hook
│   │   ├── App.jsx          # Main application component
│   │   ├── App.css          # Application styles
│   │   └── main.jsx         # Application entry point
│   ├── 📄 package.json      # Node.js dependencies
│   ├── 📄 vite.config.js    # Vite configuration
│   └── 📄 .env              # Frontend environment variables
├── 📁 .github/workflows/     # GitHub Actions CI/CD
│   └── deploy-frontend.yml  # Frontend deployment workflow
├── 📁 docs/                 # Documentation
│   ├── ARCHITECTURE.md      # System architecture
│   ├── API_REFERENCE.md     # API documentation
│   └── DEVELOPMENT.md       # This file
└── 📄 README.md             # Project overview
```

## Key Components

### Backend Components

#### EmailAgent (`email_agent.py`)
Main orchestrator for email processing.

**Key Classes:**
- `EmailAgent` - Main coordinator
- `ContextCompressor` - Thread summarization
- `SmartClassifier` - Email categorization
- `ReplyGenerator` - AI reply generation

**To modify AI behavior:**
Edit prompts in these classes to change how the AI processes emails.

#### API Server (`api_server.py`)
FastAPI routes and request handling.

**To add new endpoints:**
1. Add Pydantic model for request/response
2. Create route function with `@app` decorator
3. Implement business logic
4. Return appropriate response

### Frontend Components

#### useEmailAgent Hook (`hooks/useEmailAgent.js`)
Central state management and API calls.

**Key Functions:**
- `fetchEmails()` - Load email list
- `processEmail()` - Analyze email with AI
- `generateReply()` - Get AI-generated reply
- `sendReply()` - Send reply

#### EmailList Component (`components/EmailList.jsx`)
Displays list of emails with filtering.

**Props:**
- `emails` - Array of email objects
- `selectedEmail` - Currently selected email
- `onSelectEmail` - Callback when email clicked

#### EmailDetail Component (`components/EmailDetail.jsx`)
Shows email content and AI analysis.

**Features:**
- Email content view
- Thread view
- AI analysis (summary, key points, action items)
- Reply composer

## Common Development Tasks

### Adding a New Email Category

1. **Backend** (`email_agent.py`):
```python
class Category(Enum):
    # ... existing categories
    NEW_CATEGORY = "NewCategory"  # Add here
```

2. **Frontend** (`EmailList.jsx`):
```javascript
const getCategoryIcon = (category) => {
  const icons = {
    // ... existing icons
    NewCategory: '🆕',  // Add here
  };
};
```

### Modifying AI Prompts

Edit prompts in `email_agent.py`:

```python
# ContextCompressor
prompt = f"""Your custom prompt here..."""

# SmartClassifier  
prompt = f"""Your custom classification prompt..."""

# ReplyGenerator
prompt = f"""Your custom reply generation prompt..."""
```

### Adding a New API Endpoint

**Backend** (`api_server.py`):

```python
class NewRequest(BaseModel):
    field1: str
    field2: int

@app.post("/new-endpoint")
def new_endpoint(request: NewRequest):
    # Implementation
    return {"result": "success"}
```

**Frontend** (`useEmailAgent.js`):

```javascript
const newFunction = useCallback(async (data) => {
  const response = await fetch(`${API_BASE_URL}/new-endpoint`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return await response.json();
}, []);
```

## Testing

### Backend Testing

```bash
# Run with pytest
pip install pytest
pytest

# Test specific endpoint
curl http://localhost:8000/emails
```

### Frontend Testing

```bash
# Run tests
npm test

# Run with coverage
npm run test:coverage
```

### Manual Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend loads and connects to backend
- [ ] Email list displays correctly
- [ ] Clicking email shows details
- [ ] AI analysis generates properly
- [ ] Reply generation works
- [ ] Search filters emails
- [ ] Category filters work

## Debugging

### Backend Debugging

```python
# Add logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add breakpoints
import pdb; pdb.set_trace()
```

### Frontend Debugging

```javascript
// Add console logs
console.log('Debug:', variable);

// React DevTools
// Install browser extension for component inspection
```

### Common Issues

**Backend won't start:**
- Check Python version (3.11+)
- Verify virtual environment is activated
- Check port 8000 is not in use

**Frontend won't connect:**
- Verify backend is running
- Check `VITE_API_URL` in frontend `.env`
- Check CORS settings in backend

**AI not working:**
- Verify `GROQ_API_KEY` is set
- Check API key is valid at https://console.groq.com/
- Check rate limits not exceeded

## Building for Production

### Backend

No build step required. Deploy directly to Render.

### Frontend

```bash
cd frontend
npm run build
```

Output in `frontend/dist/` directory.

## Deployment

### Backend to Render

1. Push code to GitHub
2. Connect repo at https://dashboard.render.com/
3. Add environment variables
4. Deploy

### Frontend to GitHub Pages

1. Ensure GitHub Actions is enabled
2. Push to main branch
3. Workflow auto-deploys
4. Or manually trigger at https://github.com/Amankumar113114/AI-email_agent/actions

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes
4. Test thoroughly
5. Commit: `git commit -m "Add my feature"`
6. Push: `git push origin feature/my-feature`
7. Create Pull Request

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [Vite Docs](https://vitejs.dev/)
- [Groq Docs](https://console.groq.com/docs)

## Support

For issues or questions:
- Open an issue on GitHub
- Check existing documentation in `/docs` folder
