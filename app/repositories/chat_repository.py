import sqlite3
from typing import List

from app.core.config import settings


class ChatRepository:
    def __init__(self) -> None:
        self.db_path = settings.chat_db_path

    def get_connection(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def init_db(self) -> None:
        connection = self.get_connection()

        try:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id
                ON chat_messages(session_id)
                """
            )

            connection.commit()

        finally:
            connection.close()

    def save_message(self, session_id: str, role: str, content: str) -> None:
        connection = self.get_connection()

        try:
            connection.execute(
                """
                INSERT INTO chat_messages (session_id, role, content)
                VALUES (?, ?, ?)
                """,
                (session_id, role, content)
            )

            connection.commit()

        finally:
            connection.close()

    def get_recent_messages(self, session_id: str, limit: int) -> List[dict]:
        connection = self.get_connection()

        try:
            rows = connection.execute(
                """
                SELECT id, session_id, role, content, created_at
                FROM chat_messages
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (session_id, limit)
            ).fetchall()

            messages = [dict(row) for row in rows]
            messages.reverse()

            return messages

        finally:
            connection.close()

    def list_sessions(self) -> List[dict]:
        connection = self.get_connection()

        try:
            rows = connection.execute(
                """
                SELECT
                    session_id,
                    COUNT(*) AS messages,
                    MIN(created_at) AS first_message_at,
                    MAX(created_at) AS last_message_at
                FROM chat_messages
                GROUP BY session_id
                ORDER BY last_message_at DESC
                """
            ).fetchall()

            return [dict(row) for row in rows]

        finally:
            connection.close()

    def get_session(self, session_id: str) -> List[dict]:
        connection = self.get_connection()

        try:
            rows = connection.execute(
                """
                SELECT id, session_id, role, content, created_at
                FROM chat_messages
                WHERE session_id = ?
                ORDER BY id ASC
                """,
                (session_id,)
            ).fetchall()

            return [dict(row) for row in rows]

        finally:
            connection.close()

    def delete_session(self, session_id: str) -> int:
        connection = self.get_connection()

        try:
            cursor = connection.execute(
                """
                DELETE FROM chat_messages
                WHERE session_id = ?
                """,
                (session_id,)
            )

            connection.commit()
            return cursor.rowcount

        finally:
            connection.close()

    def get_recent_messages_all_sessions(self, limit: int) -> List[dict]:
        connection = self.get_connection()

        try:
            rows = connection.execute(
                """
                SELECT id, session_id, role, content, created_at
                FROM chat_messages
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,)
            ).fetchall()

            return [dict(row) for row in rows]

        finally:
            connection.close()