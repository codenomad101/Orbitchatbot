# SKF Orbitbot - Database Setup Guide

## 🗄️ Database Implementation Overview

The application now uses **PostgreSQL** as the primary database with **SQLAlchemy** as the ORM. The system includes comprehensive data models for users, documents, search queries, and system logging.

## 🏗️ Database Architecture

### Core Tables

1. **Users** - User authentication and profile data
2. **Documents** - Document metadata and processing status
3. **Document Chunks** - Text chunks for vector storage
4. **Search Queries** - Query history and analytics
5. **Document Access** - Access control and permissions
6. **System Logs** - Audit trail and system monitoring

### Key Features

- ✅ **PostgreSQL Integration** with connection pooling
- ✅ **JWT Authentication** with database-backed users
- ✅ **Document Management** with metadata tracking
- ✅ **Search Analytics** with query history
- ✅ **Audit Logging** for all system actions
- ✅ **Role-based Access Control** (Admin/User)
- ✅ **Background Processing** with status tracking

## 🚀 Quick Setup

### 1. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
Download and install from [postgresql.org](https://www.postgresql.org/download/windows/)

### 2. Create Database

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE orbitbot_db;
CREATE USER orbitbot_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE orbitbot_db TO orbitbot_user;
\q
```

### 3. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 4. Configure Environment

Copy the example configuration:
```bash
cp backend/config.env.example backend/.env
```

Edit `backend/.env` with your database settings:
```env
DATABASE_URL=postgresql://orbitbot_user:your_password@localhost:5432/orbitbot_db
SECRET_KEY=your-very-long-secret-key-here
```

### 5. Setup Database

```bash
cd backend
python setup_database.py setup --create-admin
```

### 6. Start the Application

```bash
# Start backend
python app.py

# Start frontend (in another terminal)
cd frontend
streamlit run streamlit_app.py
```

## 📊 Database Models

### User Model
```python
class User(Base):
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    role = Column(String(20), default="user")  # admin, user
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True))
    last_login = Column(DateTime(timezone=True))
```

### Document Model
```python
class Document(Base):
    id = Column(Integer, primary_key=True)
    filename = Column(String(255))
    original_filename = Column(String(255))
    file_type = Column(String(10))  # pdf, docx, txt
    file_size = Column(Integer)
    processing_status = Column(String(20))  # pending, processing, completed, failed
    total_chunks = Column(Integer, default=0)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True))
```

### Search Query Model
```python
class SearchQuery(Base):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    query_text = Column(Text)
    response_text = Column(Text)
    sources_used = Column(JSON)
    response_time_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True))
```

## 🔧 Database Management

### Setup Commands

```bash
# Initial setup
python setup_database.py setup

# Check database status
python setup_database.py status

# Reset database (WARNING: deletes all data)
python setup_database.py reset
```

### Manual Database Operations

```python
from database.config import SessionLocal
from database.services import UserService, DocumentService

# Get database session
db = SessionLocal()

# User operations
user_service = UserService(db)
users = user_service.get_all_users()

# Document operations
document_service = DocumentService(db)
documents = document_service.get_all_documents()

db.close()
```

## 📈 Analytics & Monitoring

### Search Analytics
- Total queries per user
- Response times
- Most queried documents
- Query success rates

### System Monitoring
- User activity logs
- Document processing status
- System performance metrics
- Error tracking

### API Endpoints

```bash
# Get search history
GET /search/history

# Get system analytics (Admin only)
GET /analytics/stats

# Get system logs (Admin only)
GET /logs/system
```

## 🔐 Security Features

### Authentication
- JWT tokens with expiration
- Password hashing with bcrypt
- Session management
- Role-based access control

### Audit Logging
- All user actions logged
- Document access tracking
- System event monitoring
- IP address and user agent logging

### Data Protection
- Encrypted password storage
- Secure token generation
- Input validation and sanitization
- SQL injection prevention

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql
   
   # Check connection settings
   python setup_database.py status
   ```

2. **Permission Denied**
   ```bash
   # Fix PostgreSQL permissions
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE orbitbot_db TO orbitbot_user;"
   ```

3. **Table Creation Failed**
   ```bash
   # Reset and recreate
   python setup_database.py reset
   ```

### Database Maintenance

```bash
# Backup database
pg_dump orbitbot_db > backup.sql

# Restore database
psql orbitbot_db < backup.sql

# Check database size
psql -c "SELECT pg_size_pretty(pg_database_size('orbitbot_db'));"
```

## 🔄 Migration from JSON to Database

The system automatically migrates from the old JSON-based authentication to the new database system:

1. **Old JSON files** are ignored once database is set up
2. **Existing vector store** continues to work with new document metadata
3. **User sessions** are preserved during migration
4. **Document processing** uses new status tracking

## 📊 Performance Considerations

### Database Optimization
- Connection pooling for better performance
- Indexed columns for faster queries
- Efficient relationship loading
- Query optimization

### Monitoring
- Database connection health checks
- Query performance monitoring
- Resource usage tracking
- Error rate monitoring

## 🛠️ Development

### Adding New Models

1. Create model in `database/models.py`
2. Add service methods in `database/services.py`
3. Update API endpoints in `app.py`
4. Run database setup to create tables

### Database Migrations

For production deployments, consider using Alembic for database migrations:

```bash
# Initialize Alembic
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migration
alembic upgrade head
```

## 📋 Production Checklist

- [ ] Change default admin password
- [ ] Set strong SECRET_KEY
- [ ] Configure production database
- [ ] Set up database backups
- [ ] Configure SSL/TLS
- [ ] Set up monitoring
- [ ] Configure log rotation
- [ ] Set up error tracking
- [ ] Configure rate limiting
- [ ] Set up health checks

## 🔗 Related Documentation

- [Authentication Guide](README_AUTH.md)
- [API Documentation](http://localhost:8000/docs)
- [Streamlit Frontend](README_FRONTEND.md)
- [Vector Store Setup](README_VECTOR.md)

---

**Need Help?** Check the troubleshooting section or create an issue in the repository.


