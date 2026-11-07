# Brand Ledger

**Every brand decision has a rule. Every AI finding has evidence. Every human decision leaves a precedent.**

A brand-governance web app that turns brand guidelines into approved, versioned, testable rules. It reviews content against these rules with evidence-cited findings, records every human decision as a precedent, and issues tamper-evident receipts.

## Architecture

```
brand-ledger/
├── frontend/              # Next.js 14 + TypeScript + Tailwind
├── backend/               # FastAPI + SQLAlchemy + PostgreSQL
├── package.json          # Monorepo root (pnpm workspaces)
└── README.md
```

## Stack

- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS, Recharts
- **Backend**: FastAPI, SQLAlchemy 2.0, PostgreSQL
- **AI (optional)**: Google Gemini or OpenAI (can be disabled)
- **Security**: JWT auth, bcrypt passwords, role-based access control (RBAC)
- **Tests**: pytest (backend), Jest (frontend)

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+
- PostgreSQL 13+
- Git

### Setup

1. **Clone and install dependencies**:
   ```bash
   git clone <repo>
   cd brand-ledger
   npm install
   ```

2. **Backend setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Database**:
   ```bash
   # Ensure PostgreSQL is running
   createdb brand_ledger
   
   # Run migrations (auto-created on first app start)
   # Tables are created automatically from SQLAlchemy models
   ```

4. **Environment variables**:
   ```bash
   # Backend
   cp backend/.env.example backend/.env
   # Edit backend/.env with your settings
   
   # Frontend
   cp frontend/.env.example frontend/.env
   ```

5. **Seed demo data**:
   ```bash
   # Run from backend directory
   python scripts/seed.py
   ```

6. **Run**:
   ```bash
   # From root (runs both frontend and backend concurrently)
   npm run dev
   
   # Or separately:
   # Terminal 1 - Backend
   cd backend
   uvicorn app.main:app --reload
   
   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

Visit:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Demo Logins

All use password: `demo1234`

- **Manager**: manager@demo.com (full access: import rules, approve, manage team, issue receipts)
- **Reviewer**: reviewer@demo.com (review submissions, override findings, comment)
- **Creator**: creator@demo.com (submit content, see findings read-only)

## Environment Variables

### Backend (`backend/.env`)

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/brand_ledger

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI (optional)
ENABLE_AI=false
AI_PROVIDER=gemini  # or openai
GEMINI_API_KEY=
OPENAI_API_KEY=

# CORS
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Rate limiting
RATE_LIMIT_REVIEW_PER_MINUTE=10
RATE_LIMIT_AI_PER_MINUTE=5

# File limits
MAX_UPLOAD_SIZE_MB=10
MAX_CONTENT_LENGTH=50000
```

### Frontend (`frontend/.env.local`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API Endpoints

### Auth
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Current user

### Rules
- `GET /api/rules/` - List rules
- `POST /api/rules/` - Create rule (manager)
- `GET /api/rules/{id}` - Get rule details
- `PATCH /api/rules/{id}` - Edit rule (creates new version, manager)
- `POST /api/rules/{id}/approve` - Approve rule (manager)
- `POST /api/rules/{id}/retire` - Retire rule (manager)

### Submissions
- `POST /api/submissions/` - Create submission
- `GET /api/submissions/{id}` - Get submission
- `GET /api/submissions/` - List submissions

### Reviews
- `POST /api/reviews/run` - Run review and evaluate submission
- `GET /api/reviews/{submission_id}/findings` - Get findings
- `POST /api/reviews/decision` - Make decision on finding (accept/override/escalate)

### Receipts
- `POST /api/receipts/approve` - Approve submission and generate receipt
- `GET /api/receipts/{id}` - Get receipt
- `POST /api/receipts/{id}/verify` - Verify receipt chain

### Guidelines
- `POST /api/guidelines/import` - Import guideline and extract rules (manager)

### Team
- `GET /api/team/users` - List users (manager)
- `PATCH /api/team/users/{id}` - Update user role (manager)

## Limits

- **File upload**: 10 MB max
- **Content length**: 50,000 characters max per submission
- **Rate limits**: 10 review requests/minute, 5 AI requests/minute per user
- **Rule types supported**: forbidden_term, pattern, required_if, max_count, ai
- **Brand score**: 100 - (15×High + 8×Medium + 4×Low) violations, minimum 0

## Rule Engine

The rule engine evaluates content deterministically before any AI involvement.

### Rule Types

1. **forbidden_term**: Whole-word, case-insensitive term matching
   ```json
   {"term": "cheap", "case_sensitive": false}
   ```

2. **pattern**: Regex-based matching
   ```json
   {"regex": "clinically proven|guaranteed|miracle"}
   ```

3. **required_if**: If trigger phrase exists, required phrase must also exist
   ```json
   {"trigger": "Save 30%", "required": "terms apply"}
   ```

4. **max_count**: Character cannot appear more than N times
   ```json
   {"character": "!", "max": 2}
   ```

5. **ai**: Tone and judgment evaluation (requires AI provider)
   ```json
   {"judgment": "warm, plain-spoken tone"}
   ```

## Roles and Permissions

| Action | Creator | Reviewer | Manager |
|--------|---------|----------|---------|
| Submit content | ✓ | ✓ | ✓ |
| View own submissions | ✓ | - | - |
| View all submissions | - | ✓ | ✓ |
| Make decisions | - | ✓ | ✓ |
| Comment on findings | - | ✓ | ✓ |
| Create rules | - | - | ✓ |
| Approve rules | - | - | ✓ |
| Retire rules | - | - | ✓ |
| Import guidelines | - | - | ✓ |
| Approve submissions | - | - | ✓ |
| Manage team roles | - | - | ✓ |
| Issue receipts | - | - | ✓ |

## Security Highlights

- Passwords hashed with bcrypt
- JWT tokens with configurable expiry
- Role-based API access (403 on permission failure)
- CORS limited to configured origins
- Input validation on all endpoints
- Max file size and content length enforced
- Tamper-evident receipt chain (SHA-256)
- AI requests never execute code in guidelines/submissions

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Deployment

### Docker

```dockerfile
# Use docker-compose.yml in repo
docker-compose up
```

### Environment-specific

Update `backend/.env` and `frontend/.env` for production URLs, API keys, secrets.

**Important**: Change `SECRET_KEY` in production.

## Known Limitations

- Single-machine deployment (no distributed receipts)
- No multilingual support
- No image review
- No real-time collaboration
- No model training

## Support

For issues or feature requests, open a GitHub issue or contact the team.

---

**Tagline**: Every brand decision has a rule. Every AI finding has evidence. Every human decision leaves a precedent.
