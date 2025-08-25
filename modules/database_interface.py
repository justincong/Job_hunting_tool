from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class DatabaseInterface(ABC):
    """Abstract base class for database operations"""
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish database connection"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Close database connection"""
        pass
    
    @abstractmethod
    def insert_document(self, collection: str, document: Dict[str, Any]) -> str:
        """Insert a document and return its ID"""
        pass
    
    @abstractmethod
    def find_documents(self, collection: str, query: Dict[str, Any] = None, 
                      limit: Optional[int] = None, sort_by: Optional[str] = None) -> List[Dict[str, Any]]:
        """Find documents matching query"""
        pass
    
    @abstractmethod
    def find_document_by_id(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Find a single document by ID"""
        pass
    
    @abstractmethod
    def update_document(self, collection: str, doc_id: str, updates: Dict[str, Any]) -> bool:
        """Update a document by ID"""
        pass
    
    @abstractmethod
    def delete_document(self, collection: str, doc_id: str) -> bool:
        """Delete a document by ID"""
        pass
    
    @abstractmethod
    def count_documents(self, collection: str, query: Dict[str, Any] = None) -> int:
        """Count documents matching query"""
        pass
    
    @abstractmethod
    def create_collection(self, collection: str) -> bool:
        """Create a new collection/table"""
        pass
    
    @abstractmethod
    def list_collections(self) -> List[str]:
        """List all collections/tables"""
        pass
    
    def add_metadata(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Add common metadata to documents"""
        document['created_at'] = datetime.utcnow().isoformat()
        document['updated_at'] = document['created_at']
        return document
    
    def update_metadata(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Add updated_at timestamp to updates"""
        updates['updated_at'] = datetime.utcnow().isoformat()
        return updates