# JobScout

**AI-Powered Resume Matching Platform**

JobScout is an intelligent job matching platform that combines advanced AI keyword extraction and sophisticated matching algorithms to connect job seekers with their ideal career opportunities.

## 🚀 Features

### 🤖 AI-Powered Resume Analysis
- **Automatic Keyword Extraction**: Advanced NLP models analyze resumes to extract relevant skills, technologies, and experience
- **Multiple Format Support**: Upload resumes in PDF, DOC, or DOCX formats
- **Real-time Processing**: Instant keyword processing with background job queue system

### 🎯 Smart Job Matching
- **Cosine Similarity Algorithms**: Advanced mathematical models calculate job-resume compatibility
- **Missing Skills Analysis**: Identify skill gaps and areas for professional development
- **Match Score Analytics**: Detailed percentage-based matching with comprehensive breakdowns
- **AI-Generated Summaries**: Contextual insights for each job match

### 🔒 Security & Privacy
- **Password Encryption**: Industry-standard bcrypt password hashing
- **Secure Sessions**: Protected user authentication with automatic session management
- **Data Privacy**: Secure file storage and encrypted data transmission

### 📊 User Experience
- **Intuitive Dashboard**: Clean, responsive interface built with NiceGUI
- **Resume Management**: Upload, download, and manage multiple resumes
- **Match Analytics**: Visual match scores, missing keywords, and detailed job information
- **Real-time Notifications**: Instant feedback on upload status and processing

## 🏗️ Architecture

### Backend (FastAPI + PostgreSQL)
```
backend/
├── src/
│   ├── routes/          # API endpoints (auth, resumes, matches)
│   ├── db/              # Database models and schemas
│   ├── processing/      # Resume processing pipeline
│   ├── matching/        # Job matching algorithms
│   ├── scraping/        # Job data collection
│   ├── models/          # Pydantic data models
│   ├── utils/           # Utilities (logging, PDF parsing, encryption)
│   └── prompts/         # AI model prompts
├── alembic/             # Database migrations
└── config.py            # Configuration management
```

### Frontend (NiceGUI)
```
frontend/
├── src/
│   ├── pages/           # UI pages (home, login, resumes, matches)
│   ├── utils/           # UI utilities and components
│   ├── api_client.py    # Backend communication
│   ├── models.py        # Frontend data models
│   └── styles.py        # UI styling
└── config.py            # Frontend configuration
```

## 🛠️ Technology Stack

### Backend Technologies
- **FastAPI**: High-performance async web framework
- **PostgreSQL**: Robust relational database with pgvector extension
- **SQLAlchemy**: Modern Python SQL toolkit with async support
- **Alembic**: Database migration management
- **AsyncPG**: High-performance PostgreSQL driver
- **Pydantic**: Data validation and serialization
- **bcrypt**: Secure password hashing
- **PyMuPDF**: PDF text extraction
- **spaCy**: Natural language processing
- **KeyBERT**: Keyword extraction algorithms
- **Ollama**: Local AI model integration

### Frontend Technologies
- **NiceGUI**: Modern Python web framework
- **Tailwind CSS**: Utility-first CSS framework
- **HTTPX**: Async HTTP client for API communication

### Infrastructure
- **Poetry**: Dependency management
- **APScheduler**: Background task scheduling

## 📦 Installation

### Prerequisites
- Python 3.10+
- PostgreSQL 12+
- Docker (optional)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd job_scout
   ```

2. **Environment Configuration (IMPORTANT)**
   
   Both the backend and frontend require environment configuration files. These files contain sensitive information and are not included in the repository.

   **Backend Environment Setup:**
   ```bash
   cd backend
   cp .env.example .env
   ```
   
   **Frontend Environment Setup:**
   ```bash
   cd frontend
   cp .env.example .env
   ```

3. **Configure Your Environment Variables**

   **Backend Configuration (`backend/.env`):**
   ```env
   # Database connection (REQUIRED)
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=jobscout
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your_secure_password_here
   
   # Application settings (REQUIRED)
   APP_HOST=127.0.0.1
   APP_PORT=8080
   RESUME_DIR=/path/to/resume/storage
   
   # External APIs (REQUIRED for job scraping)
   JOOBLE_API_KEY=your_jooble_api_key_here
   
   # Optional AI settings
   OLLAMA_HOST=http://localhost:11434
   OLLAMA_MODEL=llama3
   ```

   **Frontend Configuration (`frontend/.env`):**
   ```env
   # Backend API connection (REQUIRED)
   API_URL=http://localhost:8080
   
   # Frontend server settings (OPTIONAL)
   FRONTEND_HOST=127.0.0.1
   FRONTEND_PORT=8081
   ```

4. **Create Required Directories**
   ```bash
   # Create resume storage directory (update path to match your .env)
   mkdir -p /path/to/resume/storage
   chmod 755 /path/to/resume/storage
   ```

5. **Install Dependencies**
   ```bash
   # Backend dependencies
   cd backend
   poetry install
   
   # Frontend dependencies
   cd ../frontend
   poetry install
   ```

6. **Database Setup**
   ```bash
   cd backend
   
   # Ensure PostgreSQL is running
   # Create the database specified in your .env file
   createdb jobscout  # or whatever you named it in POSTGRES_DB
   
   # Run database migrations
   poetry run alembic upgrade head
   ```

7. **Start the Application**
   ```bash
   # Terminal 1: Start backend
   cd backend
   poetry run python src/main.py
   
   # Terminal 2: Start frontend
   cd frontend
   poetry run python src/main.py
   ```

### Docker Deployment

For Docker deployment, you still need to configure environment files:

1. **Setup Environment Files**
   ```bash
   # Copy and configure environment files
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   
   # Edit the files with your configuration
   # For Docker, use these settings in backend/.env:
   POSTGRES_HOST=postgres  # Docker service name
   API_URL=http://backend:8080  # Docker service name
   ```

2. **Deploy with Docker**
   ```bash
   # Build and start all services
   docker-compose up --build
   
   # Run in background
   docker-compose up -d
   ```

## 🔧 Configuration

### Environment Variables Explained

#### Backend Environment Variables (`backend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `POSTGRES_HOST` | ✅ | `localhost` | PostgreSQL server hostname |
| `POSTGRES_PORT` | ✅ | `5432` | PostgreSQL server port |
| `POSTGRES_DB` | ✅ | `jobscout` | Database name |
| `POSTGRES_USER` | ✅ | `postgres` | Database username |
| `POSTGRES_PASSWORD` | ✅ | - | Database password |
| `APP_HOST` | ✅ | `127.0.0.1` | Backend server host |
| `APP_PORT` | ✅ | `8080` | Backend server port |
| `RESUME_DIR` | ✅ | - | Directory for resume file storage |
| `JOOBLE_API_KEY` | ✅ | - | API key for job data scraping |
| `OLLAMA_HOST` | ❌ | `http://localhost:11434` | Ollama AI service URL |
| `OLLAMA_MODEL` | ❌ | `llama3` | Ollama model name |
| `LOG_LEVEL` | ❌ | `INFO` | Logging level |
| `DEBUG` | ❌ | `false` | Development mode |

#### Frontend Environment Variables (`frontend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_URL` | ✅ | `http://localhost:8080` | Backend API URL |
| `FRONTEND_HOST` | ❌ | `127.0.0.1` | Frontend server host |
| `FRONTEND_PORT` | ❌ | `8081` | Frontend server port |
| `DEBUG` | ❌ | `false` | Development mode |

### Getting API Keys

**Jooble API Key:**
1. Visit [Jooble API Documentation](https://jooble.org/api/about)
2. Sign up for a free account
3. Request an API key
4. Add the key to your `backend/.env` file

### Security Notes

- **Never commit `.env` files to version control**
- Use strong passwords for database access
- Keep API keys secure and rotate them regularly
- For production, consider using environment variable injection instead of `.env` files

### Troubleshooting Environment Issues

**Common Issues:**

1. **"Database connection failed"**
   - Check `POSTGRES_*` variables in `backend/.env`
   - Ensure PostgreSQL is running
   - Verify database exists

2. **"Resume directory not found"**
   - Check `RESUME_DIR` path in `backend/.env`
   - Ensure directory exists and has write permissions

3. **"API connection failed" (Frontend)**
   - Check `API_URL` in `frontend/.env`
   - Ensure backend is running on specified host/port

4. **"Missing API key" errors**
   - Verify `JOOBLE_API_KEY` is set in `backend/.env`
   - Check API key is valid and not expired

## 🔄 Processing Pipeline

1. **Resume Upload**: User uploads resume file
2. **Text Extraction**: System extracts text from PDF/DOC files
3. **AI Analysis**: NLP models extract relevant keywords and skills
4. **Query Generation**: Creates targeted job search queries based on extracted skills
5. **Job Matching**: Compares resume against job database using cosine similarity
6. **Result Generation**: Produces match scores, missing skills, and AI summaries

## 📊 Database Schema

### Core Tables
- **users**: User accounts with encrypted passwords
- **resumes**: Resume files with extracted keywords and embeddings
- **companies**: Job posting companies
- **listings**: Job postings with requirement data
- **matches**: Resume-job matches with scores and analysis
- **stored_queries**: Generated search queries for job scraping

## 🧪 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/logout` - User logout

### Resume Management
- `POST /resumes/upload` - Upload resume file
- `GET /resumes/` - List user resumes
- `GET /resumes/{id}/file` - Download resume file
- `DELETE /resumes/{id}` - Delete resume

### Job Matching
- `GET /matches/` - List job matches for user
- `GET /matches/{id}` - Get detailed match information

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Mateusz Piechowski**
- **Mariusz Rychlicki** - mariusz.rychlicki@proton.me

## 🙏 Acknowledgments

- spaCy for natural language processing capabilities
- KeyBERT for advanced keyword extraction
- FastAPI for the robust backend framework
- NiceGUI for the modern Python web interface
- PostgreSQL and pgvector for efficient similarity search

---

*JobScout - Connecting talent with opportunity through intelligent matching*