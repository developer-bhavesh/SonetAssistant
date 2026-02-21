"""Database service for chat persistence."""
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional
from app.models import ChatSession, Message, MessageRole
import json

class DatabaseService:
    """SQLite database for chat history."""
    
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = Path.home() / ".config" / "sonet" / "chat_history.db"
        
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema with optimizations."""
        with sqlite3.connect(self.db_path) as conn:
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            """)
            
            # Create indexes for performance
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_session 
                ON messages(session_id, timestamp)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_updated 
                ON sessions(updated_at DESC)
            """)
            
            conn.commit()
    
    def save_session(self, session: ChatSession):
        """Save or update session."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO sessions (id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            """, (session.id, session.title, 
                  session.created_at.isoformat(), 
                  session.updated_at.isoformat()))
            
            # Delete old messages
            conn.execute("DELETE FROM messages WHERE session_id = ?", (session.id,))
            
            # Insert messages
            for msg in session.messages:
                conn.execute("""
                    INSERT INTO messages (id, session_id, role, content, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (msg.id, session.id, msg.role.value, msg.content, 
                      msg.timestamp.isoformat()))
            
            conn.commit()
    
    def load_session(self, session_id: str) -> Optional[ChatSession]:
        """Load session by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id, title, created_at, updated_at FROM sessions WHERE id = ?",
                (session_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            
            session = ChatSession(
                id=row[0],
                title=row[1],
                created_at=datetime.fromisoformat(row[2]),
                updated_at=datetime.fromisoformat(row[3])
            )
            
            cursor = conn.execute(
                "SELECT id, role, content, timestamp FROM messages WHERE session_id = ? ORDER BY timestamp",
                (session_id,)
            )
            for msg_row in cursor.fetchall():
                session.messages.append(Message(
                    id=msg_row[0],
                    role=MessageRole(msg_row[1]),
                    content=msg_row[2],
                    timestamp=datetime.fromisoformat(msg_row[3])
                ))
            
            return session
    
    def list_sessions(self) -> list[tuple[str, str, datetime]]:
        """List all sessions (id, title, updated_at)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id, title, updated_at FROM sessions ORDER BY updated_at DESC"
            )
            return [(row[0], row[1], datetime.fromisoformat(row[2])) 
                    for row in cursor.fetchall()]
    
    def delete_session(self, session_id: str):
        """Delete session and its messages."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            conn.commit()
