from typing import Dict, List, Any, Optional
from .database_interface import DatabaseInterface
from datetime import datetime
import os

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, PyMongoError
    from bson import ObjectId
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False
    MongoClient = None
    ConnectionFailure = Exception
    PyMongoError = Exception
    ObjectId = None

class MongoDatabase(DatabaseInterface):
    """MongoDB implementation of DatabaseInterface"""
    
    def __init__(self, connection_string: str = None, database_name: str = "resume_builder"):
        if not PYMONGO_AVAILABLE:
            raise ImportError("pymongo not installed. Run: pip install pymongo[srv]")
        
        self.connection_string = connection_string or os.getenv('MONGODB_CONNECTION_STRING')
        self.database_name = database_name
        self.client = None
        self.database = None
        
        if not self.connection_string:
            raise ValueError("MongoDB connection string not provided. Set MONGODB_CONNECTION_STRING environment variable or pass connection_string parameter.")
    
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            self.database = self.client[self.database_name]
            return True
        except ConnectionFailure as e:
            print(f"MongoDB connection failed: {e}")
            return False
        except Exception as e:
            print(f"MongoDB connection error: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            self.client = None
            self.database = None
    
    def insert_document(self, collection: str, document: Dict[str, Any]) -> str:
        """Insert a document and return its ID"""
        if not self.database:
            raise Exception("Database not connected")
        
        document = self.add_metadata(document)
        
        try:
            collection_obj = self.database[collection]
            result = collection_obj.insert_one(document)
            return str(result.inserted_id)
        except PyMongoError as e:
            raise Exception(f"Failed to insert document: {e}")
    
    def find_documents(self, collection: str, query: Dict[str, Any] = None, 
                      limit: Optional[int] = None, sort_by: Optional[str] = None) -> List[Dict[str, Any]]:
        """Find documents matching query"""
        if not self.database:
            raise Exception("Database not connected")
        
        try:
            collection_obj = self.database[collection]
            
            # Convert _id string to ObjectId if present in query
            if query and '_id' in query:
                if isinstance(query['_id'], str):
                    query['_id'] = ObjectId(query['_id'])
            
            cursor = collection_obj.find(query or {})
            
            # Apply sorting
            if sort_by:
                if sort_by.startswith('-'):
                    cursor = cursor.sort(sort_by[1:], -1)  # Descending
                else:
                    cursor = cursor.sort(sort_by, 1)  # Ascending
            
            # Apply limit
            if limit:
                cursor = cursor.limit(limit)
            
            # Convert ObjectId to string for JSON serialization
            documents = []
            for doc in cursor:
                doc['_id'] = str(doc['_id'])
                documents.append(doc)
            
            return documents
        except PyMongoError as e:
            raise Exception(f"Failed to find documents: {e}")
    
    def find_document_by_id(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Find a single document by ID"""
        if not self.database:
            raise Exception("Database not connected")
        
        try:
            collection_obj = self.database[collection]
            
            # Convert string ID to ObjectId
            object_id = ObjectId(doc_id) if ObjectId.is_valid(doc_id) else doc_id
            
            document = collection_obj.find_one({"_id": object_id})
            
            if document:
                document['_id'] = str(document['_id'])
                return document
            
            return None
        except PyMongoError as e:
            raise Exception(f"Failed to find document: {e}")
    
    def update_document(self, collection: str, doc_id: str, updates: Dict[str, Any]) -> bool:
        """Update a document by ID"""
        if not self.database:
            raise Exception("Database not connected")
        
        try:
            collection_obj = self.database[collection]
            
            # Convert string ID to ObjectId
            object_id = ObjectId(doc_id) if ObjectId.is_valid(doc_id) else doc_id
            
            # Add updated_at timestamp
            updates = self.update_metadata(updates)
            
            result = collection_obj.update_one(
                {"_id": object_id},
                {"$set": updates}
            )
            
            return result.modified_count > 0
        except PyMongoError as e:
            raise Exception(f"Failed to update document: {e}")
    
    def delete_document(self, collection: str, doc_id: str) -> bool:
        """Delete a document by ID"""
        if not self.database:
            raise Exception("Database not connected")
        
        try:
            collection_obj = self.database[collection]
            
            # Convert string ID to ObjectId
            object_id = ObjectId(doc_id) if ObjectId.is_valid(doc_id) else doc_id
            
            result = collection_obj.delete_one({"_id": object_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            raise Exception(f"Failed to delete document: {e}")
    
    def count_documents(self, collection: str, query: Dict[str, Any] = None) -> int:
        """Count documents matching query"""
        if not self.database:
            raise Exception("Database not connected")
        
        try:
            collection_obj = self.database[collection]
            
            # Convert _id string to ObjectId if present in query
            if query and '_id' in query:
                if isinstance(query['_id'], str):
                    query['_id'] = ObjectId(query['_id'])
            
            return collection_obj.count_documents(query or {})
        except PyMongoError as e:
            raise Exception(f"Failed to count documents: {e}")
    
    def create_collection(self, collection: str) -> bool:
        """Create a new collection"""
        if not self.database:
            raise Exception("Database not connected")
        
        try:
            # In MongoDB, collections are created automatically when first document is inserted
            # But we can explicitly create it
            self.database.create_collection(collection)
            return True
        except PyMongoError as e:
            # Collection might already exist
            if "already exists" in str(e).lower():
                return True
            raise Exception(f"Failed to create collection: {e}")
    
    def list_collections(self) -> List[str]:
        """List all collections"""
        if not self.database:
            raise Exception("Database not connected")
        
        try:
            return self.database.list_collection_names()
        except PyMongoError as e:
            raise Exception(f"Failed to list collections: {e}")
    
    def create_indexes(self, collection: str, indexes: List[Dict[str, Any]]):
        """Create indexes for better query performance"""
        if not self.database:
            raise Exception("Database not connected")
        
        try:
            collection_obj = self.database[collection]
            for index in indexes:
                collection_obj.create_index([(index['field'], index.get('order', 1))])
        except PyMongoError as e:
            print(f"Warning: Failed to create indexes: {e}")
    
    @staticmethod
    def get_connection_string_template() -> str:
        """Get MongoDB Atlas connection string template"""
        return "mongodb+srv://<username>:<password>@<cluster-url>/<database>?retryWrites=true&w=majority"