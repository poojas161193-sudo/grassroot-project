# Database Implementation Guide

## Current Database Implementation

### 🗄️ **Database Technology: SQLite**

The Video Analyzer project currently uses **SQLite** as the database system with the following configuration:

```python
DATABASE_URL = config('DATABASE_URL', default='sqlite:///./video_analyzer.db')
```

### 📊 **Database Schema**

#### 1. **Videos Table**
```sql
CREATE TABLE videos (
    id INTEGER PRIMARY KEY,           -- Auto-incrementing video ID
    filename VARCHAR,                 -- Original video filename  
    file_path VARCHAR,               -- Path to stored video file
    transcription TEXT,              -- Full audio transcription
    summary TEXT,                    -- AI-generated summary
    uploaded_at DATETIME             -- Upload timestamp
);
```

#### 2. **Chat History Table**
```sql
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY,          -- Auto-incrementing chat ID
    video_id INTEGER,               -- Foreign key to videos table
    question TEXT,                  -- User question
    answer TEXT,                    -- AI-generated answer
    timestamp DATETIME              -- Question timestamp
);
```

### 🔧 **SQLAlchemy ORM Implementation**

**Models Definition (`models.py`):**
- Uses SQLAlchemy ORM for database abstraction
- Declarative base pattern for model definitions
- Session management with dependency injection
- Automatic table creation on startup

**Key Features:**
- **Connection Pool**: Handles multiple concurrent requests
- **Session Management**: Automatic session cleanup
- **Index Optimization**: Indexed columns for faster queries
- **Data Types**: Proper type mapping (String, Text, DateTime, Integer)

### 💾 **Data Storage Strategy**

1. **Video Files**: Stored in filesystem (`./uploads/` directory)
2. **Metadata**: Video information stored in database
3. **Transcriptions**: Full text stored as TEXT fields
4. **Chat History**: All Q&A interactions preserved

## Production Database Options

### 🚀 **1. PostgreSQL (Recommended for Production)**

**Configuration:**
```python
# .env
DATABASE_URL=postgresql://username:password@host:5432/video_analyzer

# requirements.txt
psycopg2-binary==2.9.7
```

**Advantages:**
- ✅ High performance and scalability
- ✅ ACID compliance
- ✅ Advanced indexing (full-text search)
- ✅ JSON support for metadata
- ✅ Concurrent connections
- ✅ Built-in backup and replication

**Migration Example:**
```python
# Enhanced models for PostgreSQL
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), index=True)
    file_path = Column(String(500))
    transcription = Column(Text)
    summary = Column(Text)
    metadata = Column(JSON)  # Additional video metadata
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Full-text search index
    __table_args__ = (
        Index('ix_transcription_fts', 'transcription', postgresql_using='gin'),
    )
```

### 🔥 **2. Redis + PostgreSQL Hybrid**

**Use Case**: High-traffic applications

**Configuration:**
```python
# Primary database: PostgreSQL
DATABASE_URL=postgresql://username:password@host:5432/video_analyzer

# Cache layer: Redis
REDIS_URL=redis://localhost:6379/0
```

**Implementation:**
- **PostgreSQL**: Persistent data storage
- **Redis**: Session caching, temporary data, pub/sub for real-time features

### ☁️ **3. Cloud Database Solutions**

#### **AWS RDS PostgreSQL**
```python
DATABASE_URL=postgresql://username:password@your-db.123456789012.us-east-1.rds.amazonaws.com:5432/video_analyzer
```

#### **Google Cloud SQL**
```python
DATABASE_URL=postgresql://username:password@/video_analyzer?host=/cloudsql/project:region:instance
```

#### **Azure Database for PostgreSQL**
```python
DATABASE_URL=postgresql://username%40servername:password@servername.postgres.database.azure.com:5432/video_analyzer
```

### 🗃️ **4. NoSQL Options**

#### **MongoDB** (Document-based)
```python
# For flexible schema and JSON-heavy data
MONGODB_URL=mongodb://username:password@host:27017/video_analyzer
```

**Schema Example:**
```python
{
    "_id": ObjectId("..."),
    "filename": "video.mp4",
    "file_path": "/uploads/video.mp4",
    "transcription": "...",
    "summary": "...",
    "chat_history": [
        {
            "question": "What is this video about?",
            "answer": "...",
            "timestamp": "2024-01-01T12:00:00Z"
        }
    ],
    "uploaded_at": "2024-01-01T10:00:00Z",
    "metadata": {
        "duration": 300,
        "size": 52428800,
        "format": "mp4"
    }
}
```

## Production Migration Strategy

### 📋 **Step 1: Database Migration**

```python
# database/migration.py
from sqlalchemy import create_engine
import sqlite3
import psycopg2

def migrate_sqlite_to_postgresql():
    # Export from SQLite
    sqlite_conn = sqlite3.connect('video_analyzer.db')
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connect to PostgreSQL
    pg_engine = create_engine(POSTGRESQL_URL)
    
    # Migrate videos table
    videos = sqlite_cursor.execute("SELECT * FROM videos").fetchall()
    for video in videos:
        # Insert into PostgreSQL with proper data transformation
        pass
    
    # Migrate chat_history table
    # Similar process...
```

### 📊 **Step 2: Environment Configuration**

```bash
# Development
DATABASE_URL=sqlite:///./video_analyzer.db

# Staging
DATABASE_URL=postgresql://user:pass@staging-db:5432/video_analyzer

# Production
DATABASE_URL=postgresql://user:pass@prod-db:5432/video_analyzer
```

### 🔒 **Step 3: Security Enhancements**

```python
# production_models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from werkzeug.security import generate_password_hash

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))  # User ownership
    filename = Column(String(255), index=True)
    is_public = Column(Boolean, default=False)  # Privacy control
    # ... other fields
```

## Performance Optimization

### 🚀 **Database Indexing Strategy**

```sql
-- Full-text search on transcriptions
CREATE INDEX idx_transcription_fts ON videos USING gin(to_tsvector('english', transcription));

-- User queries optimization  
CREATE INDEX idx_video_user_id ON videos(user_id);
CREATE INDEX idx_chat_video_id ON chat_history(video_id);

-- Time-based queries
CREATE INDEX idx_videos_uploaded_at ON videos(uploaded_at DESC);
CREATE INDEX idx_chat_timestamp ON chat_history(timestamp DESC);
```

### 📊 **Connection Pool Configuration**

```python
# production_database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,          # Number of connections to maintain
    max_overflow=30,       # Additional connections under load
    pool_recycle=1800,     # Recycle connections every 30 minutes
    pool_pre_ping=True     # Validate connections before use
)
```

## Backup and Recovery Strategy

### 💾 **PostgreSQL Backup**

```bash
# Daily automated backup
pg_dump -h host -U username -d video_analyzer > backup_$(date +%Y%m%d).sql

# Point-in-time recovery setup
wal_level = replica
archive_mode = on
archive_command = 'cp %p /backup/archive/%f'
```

### ☁️ **Cloud Backup Options**

- **AWS RDS**: Automated backups, point-in-time recovery
- **Google Cloud SQL**: Automatic backups, replicas
- **Azure Database**: Geo-redundant backups

## Monitoring and Analytics

### 📈 **Database Metrics**

```python
# monitoring.py
from sqlalchemy import text
from datetime import datetime, timedelta

def get_database_stats(db):
    stats = {}
    
    # Total videos processed
    stats['total_videos'] = db.execute(text("SELECT COUNT(*) FROM videos")).scalar()
    
    # Videos processed today
    today = datetime.utcnow().date()
    stats['videos_today'] = db.execute(
        text("SELECT COUNT(*) FROM videos WHERE DATE(uploaded_at) = :today"),
        {"today": today}
    ).scalar()
    
    # Average processing time
    # Chat interactions
    stats['total_chats'] = db.execute(text("SELECT COUNT(*) FROM chat_history")).scalar()
    
    return stats
```

## Cost Considerations

### 💰 **Database Hosting Costs (Monthly Estimates)**

| Option | Small (1-100 users) | Medium (100-1K users) | Large (1K+ users) |
|--------|---------------------|------------------------|-------------------|
| SQLite | $0 (local) | Not recommended | Not recommended |
| PostgreSQL (Self-hosted) | $10-20 | $50-100 | $200+ |
| AWS RDS | $15-30 | $100-200 | $500+ |
| Google Cloud SQL | $10-25 | $80-150 | $400+ |
| Azure Database | $12-28 | $90-180 | $450+ |

### 🎯 **Recommendation by Scale**

- **Development/Testing**: SQLite (current setup)
- **Small Production**: PostgreSQL on VPS
- **Medium Production**: Managed PostgreSQL (AWS RDS/Google Cloud SQL)
- **Large Production**: PostgreSQL cluster + Redis caching
- **Enterprise**: Multi-region setup with read replicas

The current SQLite implementation is perfect for development and small deployments, but for production scaling, PostgreSQL offers the best balance of performance, features, and ecosystem support.