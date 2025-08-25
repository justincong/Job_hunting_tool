import sqlite3
import json
import uuid
from typing import Dict, List, Any, Optional
from .database_interface import DatabaseInterface
import os

class SQLiteDatabase(DatabaseInterface):
    """SQLite implementation of DatabaseInterface"""
    
    def __init__(self, db_path: str = "resume_builder.db"):
        self.db_path = db_path
        self.connection = None
        
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Enable dict-like access
            return True
        except Exception as e:
            print(f"SQLite connection error: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def _ensure_table_exists(self, collection: str):
        """Create table if it doesn't exist"""
        cursor = self.connection.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {collection} (
                id TEXT PRIMARY KEY,
                document TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        self.connection.commit()
    
    def insert_document(self, collection: str, document: Dict[str, Any]) -> str:
        """Insert a document and return its ID"""
        if not self.connection:
            raise Exception("Database not connected")
        
        self._ensure_table_exists(collection)
        
        doc_id = str(uuid.uuid4())
        document = self.add_metadata(document)
        document['_id'] = doc_id
        
        cursor = self.connection.cursor()
        cursor.execute(f'''
            INSERT INTO {collection} (id, document, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (doc_id, json.dumps(document), document['created_at'], document['updated_at']))
        
        self.connection.commit()
        return doc_id
    
    def find_documents(self, collection: str, query: Dict[str, Any] = None, 
                      limit: Optional[int] = None, sort_by: Optional[str] = None) -> List[Dict[str, Any]]:
        """Find documents matching query"""
        if not self.connection:
            raise Exception("Database not connected")
        
        self._ensure_table_exists(collection)
        
        cursor = self.connection.cursor()
        sql = f"SELECT document FROM {collection}"
        
        # Add WHERE clause if query provided
        where_conditions = []
        params = []
        
        if query:
            for key, value in query.items():
                if key == '_id':
                    where_conditions.append("id = ?")
                    params.append(value)
                else:
                    # For JSON fields, use JSON extract (SQLite 3.45+) or simple text search
                    where_conditions.append(f"document LIKE ?")
                    params.append(f'%"{key}":"{value}"%')
        
        if where_conditions:
            sql += " WHERE " + " AND ".join(where_conditions)
        
        # Add ORDER BY
        if sort_by:
            if sort_by.startswith('-'):
                sql += f" ORDER BY {sort_by[1:]} DESC"
            else:
                sql += f" ORDER BY {sort_by} ASC"
        
        # Add LIMIT
        if limit:
            sql += f" LIMIT {limit}"
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        return [json.loads(row['document']) for row in rows]
    
    def find_document_by_id(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Find a single document by ID"""
        if not self.connection:
            raise Exception("Database not connected")
        
        self._ensure_table_exists(collection)
        
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT document FROM {collection} WHERE id = ?", (doc_id,))
        row = cursor.fetchone()
        
        if row:
            return json.loads(row['document'])
        return None
    
    def update_document(self, collection: str, doc_id: str, updates: Dict[str, Any]) -> bool:
        """Update a document by ID"""
        if not self.connection:
            raise Exception("Database not connected")
        
        # Get existing document
        existing_doc = self.find_document_by_id(collection, doc_id)
        if not existing_doc:
            return False
        
        # Apply updates
        existing_doc.update(updates)
        existing_doc = self.update_metadata(existing_doc)
        
        cursor = self.connection.cursor()
        cursor.execute(f'''
            UPDATE {collection} 
            SET document = ?, updated_at = ?
            WHERE id = ?
        ''', (json.dumps(existing_doc), existing_doc['updated_at'], doc_id))
        
        self.connection.commit()
        return cursor.rowcount > 0
    
    def delete_document(self, collection: str, doc_id: str) -> bool:
        """Delete a document by ID"""
        if not self.connection:
            raise Exception("Database not connected")
        
        cursor = self.connection.cursor()
        cursor.execute(f"DELETE FROM {collection} WHERE id = ?", (doc_id,))
        self.connection.commit()
        return cursor.rowcount > 0
    
    def count_documents(self, collection: str, query: Dict[str, Any] = None) -> int:
        """Count documents matching query"""
        if not self.connection:
            raise Exception("Database not connected")
        
        self._ensure_table_exists(collection)
        
        cursor = self.connection.cursor()
        sql = f"SELECT COUNT(*) FROM {collection}"
        params = []
        
        if query:
            where_conditions = []
            for key, value in query.items():
                if key == '_id':
                    where_conditions.append("id = ?")
                    params.append(value)
                else:
                    where_conditions.append(f"document LIKE ?")
                    params.append(f'%"{key}":"{value}"%')
            
            if where_conditions:
                sql += " WHERE " + " AND ".join(where_conditions)
        
        cursor.execute(sql, params)
        return cursor.fetchone()[0]
    
    def create_collection(self, collection: str) -> bool:
        """Create a new collection/table"""
        try:
            self._ensure_table_exists(collection)
            return True
        except Exception:
            return False
    
    def list_collections(self) -> List[str]:
        """List all collections/tables"""
        if not self.connection:
            raise Exception("Database not connected")
        
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in cursor.fetchall()]