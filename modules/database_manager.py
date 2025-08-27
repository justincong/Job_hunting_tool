import os
import json
from typing import Dict, Any, Optional
from .database_interface import DatabaseInterface
from .sqlite_database import SQLiteDatabase
from .mongodb_database import MongoDatabase

class DatabaseManager:
    """Manages database connections and switching between different database types"""
    
    def __init__(self):
        self.current_db: Optional[DatabaseInterface] = None
        self.config_file = "database_config.json"
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load database configuration from file"""
        default_config = {
            "active_database": "sqlite",
            "sqlite": {
                "db_path": "resume_builder.db"
            },
            "mongodb": {
                "connection_string": "",
                "database_name": "resume_builder"
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults to ensure all keys exist
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                print(f"Error loading database config: {e}")
                return default_config
        else:
            self._save_config(default_config)
            return default_config
    
    def _save_config(self, config: Dict[str, Any]):
        """Save database configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving database config: {e}")
    
    def get_available_databases(self) -> Dict[str, str]:
        """Get list of available database types"""
        databases = {
            "sqlite": "SQLite (Local)"
        }
        
        # Check if MongoDB is available
        try:
            from .mongodb_database import PYMONGO_AVAILABLE
            if PYMONGO_AVAILABLE:
                databases["mongodb"] = "MongoDB (Cloud)"
            else:
                databases["mongodb"] = "MongoDB (Not Available - install pymongo)"
        except ImportError:
            databases["mongodb"] = "MongoDB (Not Available - install pymongo)"
        
        return databases
    
    def switch_database(self, db_type: str) -> bool:
        """Switch to a different database type"""
        try:
            # Disconnect current database
            if self.current_db:
                self.current_db.disconnect()
                self.current_db = None
            
            # Create new database instance
            if db_type == "sqlite":
                db_path = self.config["sqlite"]["db_path"]
                self.current_db = SQLiteDatabase(db_path)
            elif db_type == "mongodb":
                connection_string = self.config["mongodb"]["connection_string"]
                database_name = self.config["mongodb"]["database_name"]
                
                if not connection_string:
                    raise ValueError("MongoDB connection string not configured")
                
                self.current_db = MongoDatabase(connection_string, database_name)
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
            
            # Test connection
            if self.current_db.connect():
                self.config["active_database"] = db_type
                self._save_config(self.config)
                return True
            else:
                self.current_db = None
                return False
                
        except Exception as e:
            print(f"Error switching database: {e}")
            self.current_db = None
            return False
    
    def get_database(self) -> Optional[DatabaseInterface]:
        """Get current database instance"""
        if not self.current_db:
            # Try to initialize with the configured database
            db_type = self.config["active_database"]
            if not self.switch_database(db_type):
                # If configured database fails, fallback to SQLite
                if db_type != "sqlite":
                    print(f"Failed to connect to {db_type}, falling back to SQLite")
                    self.switch_database("sqlite")
        
        return self.current_db
    
    def update_mongodb_config(self, connection_string: str, database_name: str = "resume_builder"):
        """Update MongoDB configuration"""
        self.config["mongodb"]["connection_string"] = connection_string
        self.config["mongodb"]["database_name"] = database_name
        self._save_config(self.config)
    
    def update_sqlite_config(self, db_path: str = "resume_builder.db"):
        """Update SQLite configuration"""
        self.config["sqlite"]["db_path"] = db_path
        self._save_config(self.config)
    
    def get_current_database_type(self) -> str:
        """Get currently active database type"""
        return self.config["active_database"]
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get information about current database"""
        db_type = self.config["active_database"]
        info = {
            "type": db_type,
            "connected": self.current_db is not None
        }
        
        if db_type == "sqlite":
            info["path"] = self.config["sqlite"]["db_path"]
            info["file_exists"] = os.path.exists(self.config["sqlite"]["db_path"])
        elif db_type == "mongodb":
            info["database_name"] = self.config["mongodb"]["database_name"]
            info["has_connection_string"] = bool(self.config["mongodb"]["connection_string"])
        
        return info
    
    def test_connection(self, db_type: str = None) -> bool:
        """Test database connection"""
        if db_type is None:
            db_type = self.config["active_database"]
        
        temp_db = None
        try:
            if db_type == "sqlite":
                temp_db = SQLiteDatabase(self.config["sqlite"]["db_path"])
            elif db_type == "mongodb":
                connection_string = self.config["mongodb"]["connection_string"]
                database_name = self.config["mongodb"]["database_name"]
                if not connection_string:
                    return False
                temp_db = MongoDatabase(connection_string, database_name)
            
            if temp_db:
                result = temp_db.connect()
                temp_db.disconnect()
                return result
            
            return False
        except Exception:
            return False
    
    def initialize_collections(self):
        """Initialize required collections/tables"""
        db = self.get_database()
        if not db:
            return False
        
        collections = [
            "job_analyses",
            "resumes", 
            "profiles",
            "templates"
        ]
        
        try:
            for collection in collections:
                db.create_collection(collection)
            
            # Create indexes for MongoDB
            if isinstance(db, MongoDatabase):
                # Index for job analyses
                db.create_indexes("job_analyses", [
                    {"field": "created_at"},
                    {"field": "job_title"},
                    {"field": "company"}
                ])
            
            return True
        except Exception as e:
            print(f"Error initializing collections: {e}")
            return False

# Global database manager instance
db_manager = DatabaseManager()

# Auto-initialize SQLite connection on startup
try:
    if not db_manager.get_database():
        print("Warning: Could not initialize any database connection")
    else:
        db_manager.initialize_collections()
except Exception as e:
    print(f"Error during database initialization: {e}")