"""
AI Memory Service - Persistent memory for stock research and analysis.
Inspired by Stitch AI for maintaining context across sessions.
"""
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path

from ..utils.config import DB_PATH


class AIMemory:
    """
    Persistent AI memory for stock research.

    Stores:
    - Research findings about stocks
    - User preferences and patterns
    - Chat conversation history
    - Analysis insights that should persist
    """

    def __init__(self):
        self._init_memory_tables()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_memory_tables(self):
        """Initialize memory tables in database."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Stock research memory
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_stock_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                content TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 1
            )
        """)

        # Create index for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_stock_memory_symbol
            ON ai_stock_memory(symbol)
        """)

        # General knowledge memory
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_knowledge_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, key)
            )
        """)

        # Conversation memory
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_conversation_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                context TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # User preferences
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_user_preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    # =========================================================================
    # Stock Research Memory
    # =========================================================================

    def remember_stock_insight(
        self,
        symbol: str,
        memory_type: str,
        content: str,
        confidence: float = 0.5,
        source: str = None
    ):
        """
        Store an insight about a stock.

        Args:
            symbol: Stock ticker
            memory_type: Type of memory (analysis, news, thesis, risk, catalyst, etc.)
            content: The insight to remember
            confidence: Confidence level 0-1
            source: Where this insight came from
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO ai_stock_memory (symbol, memory_type, content, confidence, source)
            VALUES (?, ?, ?, ?, ?)
        """, (symbol.upper(), memory_type, content, confidence, source))

        conn.commit()
        conn.close()

    def recall_stock_memories(
        self,
        symbol: str,
        memory_type: str = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Recall memories about a stock.

        Args:
            symbol: Stock ticker
            memory_type: Filter by type (optional)
            limit: Max memories to return

        Returns:
            List of memory dicts
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if memory_type:
            cursor.execute("""
                SELECT * FROM ai_stock_memory
                WHERE symbol = ? AND memory_type = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (symbol.upper(), memory_type, limit))
        else:
            cursor.execute("""
                SELECT * FROM ai_stock_memory
                WHERE symbol = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (symbol.upper(), limit))

        rows = cursor.fetchall()

        # Update access count and timestamp
        for row in rows:
            cursor.execute("""
                UPDATE ai_stock_memory
                SET access_count = access_count + 1, last_accessed = ?
                WHERE id = ?
            """, (datetime.now(), row['id']))

        conn.commit()
        conn.close()

        return [dict(row) for row in rows]

    def get_all_stock_insights(self, symbol: str) -> str:
        """Get all memories for a stock as a formatted string for AI context."""
        memories = self.recall_stock_memories(symbol, limit=20)

        if not memories:
            return f"No previous research found for {symbol}."

        formatted = f"Previous research on {symbol}:\n\n"
        for m in memories:
            formatted += f"[{m['memory_type'].upper()}] ({m['created_at'][:10]})\n"
            formatted += f"{m['content']}\n"
            formatted += f"Confidence: {m['confidence']:.0%} | Source: {m['source'] or 'AI Analysis'}\n\n"

        return formatted

    # =========================================================================
    # Knowledge Memory
    # =========================================================================

    def store_knowledge(
        self,
        category: str,
        key: str,
        value: Any,
        metadata: Dict = None
    ):
        """
        Store general knowledge.

        Args:
            category: Category (sector_info, market_trends, user_patterns, etc.)
            key: Unique key within category
            value: Value to store (will be JSON serialized)
            metadata: Optional metadata dict
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        value_json = json.dumps(value) if not isinstance(value, str) else value
        metadata_json = json.dumps(metadata) if metadata else None

        cursor.execute("""
            INSERT INTO ai_knowledge_memory (category, key, value, metadata, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(category, key) DO UPDATE SET
                value = excluded.value,
                metadata = excluded.metadata,
                updated_at = excluded.updated_at
        """, (category, key, value_json, metadata_json, datetime.now()))

        conn.commit()
        conn.close()

    def retrieve_knowledge(self, category: str, key: str = None) -> Any:
        """
        Retrieve knowledge.

        Args:
            category: Category to retrieve
            key: Specific key (optional, returns all in category if None)

        Returns:
            Value(s) from knowledge base
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if key:
            cursor.execute("""
                SELECT value FROM ai_knowledge_memory
                WHERE category = ? AND key = ?
            """, (category, key))
            row = cursor.fetchone()
            conn.close()

            if row:
                try:
                    return json.loads(row['value'])
                except:
                    return row['value']
            return None
        else:
            cursor.execute("""
                SELECT key, value FROM ai_knowledge_memory
                WHERE category = ?
            """, (category,))
            rows = cursor.fetchall()
            conn.close()

            result = {}
            for row in rows:
                try:
                    result[row['key']] = json.loads(row['value'])
                except:
                    result[row['key']] = row['value']
            return result

    # =========================================================================
    # Conversation Memory
    # =========================================================================

    def save_conversation(
        self,
        role: str,
        content: str,
        session_id: str = None,
        context: Dict = None
    ):
        """Save a conversation message."""
        conn = self._get_connection()
        cursor = conn.cursor()

        context_json = json.dumps(context) if context else None

        cursor.execute("""
            INSERT INTO ai_conversation_memory (session_id, role, content, context)
            VALUES (?, ?, ?, ?)
        """, (session_id, role, content, context_json))

        conn.commit()
        conn.close()

    def get_conversation_history(
        self,
        session_id: str = None,
        limit: int = 20
    ) -> List[Dict]:
        """Get recent conversation history."""
        conn = self._get_connection()
        cursor = conn.cursor()

        if session_id:
            cursor.execute("""
                SELECT * FROM ai_conversation_memory
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (session_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM ai_conversation_memory
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in reversed(rows)]

    # =========================================================================
    # User Preferences
    # =========================================================================

    def set_preference(self, key: str, value: Any):
        """Set a user preference."""
        conn = self._get_connection()
        cursor = conn.cursor()

        value_json = json.dumps(value) if not isinstance(value, str) else value

        cursor.execute("""
            INSERT INTO ai_user_preferences (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = excluded.updated_at
        """, (key, value_json, datetime.now()))

        conn.commit()
        conn.close()

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT value FROM ai_user_preferences WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()

        if row:
            try:
                return json.loads(row['value'])
            except:
                return row['value']
        return default

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def get_context_for_symbol(self, symbol: str) -> str:
        """
        Get full AI context for a symbol including all memories.
        Useful for enriching AI prompts with historical knowledge.
        """
        context_parts = []

        # Stock-specific memories
        stock_memories = self.get_all_stock_insights(symbol)
        if stock_memories:
            context_parts.append(stock_memories)

        # User preferences
        prefs = self.get_preference('favorite_sectors')
        if prefs:
            context_parts.append(f"User's favorite sectors: {prefs}")

        return "\n\n---\n\n".join(context_parts)

    def cleanup_old_memories(self, days: int = 90):
        """Remove memories older than specified days that haven't been accessed."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM ai_stock_memory
            WHERE last_accessed < datetime('now', ?)
            AND access_count < 3
        """, (f'-{days} days',))

        deleted = cursor.rowcount
        conn.commit()
        conn.close()

        return deleted

    def get_memory_stats(self) -> Dict:
        """Get statistics about stored memories."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM ai_stock_memory")
        stock_memories = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM ai_knowledge_memory")
        knowledge = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM ai_conversation_memory")
        conversations = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(DISTINCT symbol) as count FROM ai_stock_memory")
        unique_stocks = cursor.fetchone()['count']

        conn.close()

        return {
            'stock_memories': stock_memories,
            'knowledge_entries': knowledge,
            'conversation_messages': conversations,
            'unique_stocks_researched': unique_stocks
        }


# Singleton instance
ai_memory = AIMemory()
