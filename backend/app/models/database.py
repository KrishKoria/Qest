from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    client: Optional[AsyncIOMotorClient] = None
    sync_client: Optional[MongoClient] = None
    database = None
    sync_database = None

    @classmethod
    def get_connection_string(cls) -> str:
        """Get MongoDB connection string from environment variables."""
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        return mongodb_url

    @classmethod
    def get_database_name(cls) -> str:
        """Get database name from environment variables."""
        return os.getenv("DATABASE_NAME", "fitness_studio")

    @classmethod
    async def connect_to_mongo(cls):
        """Create async database connection."""
        logger.info("Connecting to MongoDB (async)...")
        connection_string = cls.get_connection_string()
        database_name = cls.get_database_name()
        
        cls.client = AsyncIOMotorClient(connection_string)
        cls.database = cls.client[database_name]
        logger.info(f"Connected to MongoDB database: {database_name}")

    @classmethod
    def connect_to_mongo_sync(cls):
        """Create sync database connection for tools."""
        logger.info("Connecting to MongoDB (sync)...")
        connection_string = cls.get_connection_string()
        database_name = cls.get_database_name()
        
        cls.sync_client = MongoClient(connection_string)
        cls.sync_database = cls.sync_client[database_name]
        logger.info(f"Connected to MongoDB database (sync): {database_name}")

    @classmethod
    async def close_mongo_connection(cls):
        """Close async database connection."""
        if cls.client:
            cls.client.close()
            logger.info("Disconnected from MongoDB (async)")

    @classmethod
    def close_mongo_connection_sync(cls):
        """Close sync database connection."""
        if cls.sync_client:
            cls.sync_client.close()
            logger.info("Disconnected from MongoDB (sync)")

    @classmethod
    def get_database(cls):
        """Get async database instance."""
        if cls.database is None:
            raise RuntimeError("Database not connected. Call connect_to_mongo first.")
        return cls.database

    @classmethod
    def get_sync_database(cls):
        """Get sync database instance."""
        if cls.sync_database is None:
            raise RuntimeError("Sync database not connected. Call connect_to_mongo_sync first.")
        return cls.sync_database


# Database collections
class Collections:
    CLIENTS = "clients"
    ORDERS = "orders"
    PAYMENTS = "payments"
    COURSES = "courses"
    CLASSES = "classes"
    ATTENDANCE = "attendance"


# Helper functions for database operations
def get_collection(collection_name: str):
    """Get async collection instance."""
    db = DatabaseManager.get_database()
    return db[collection_name]


def get_sync_collection(collection_name: str):
    """Get sync collection instance."""
    db = DatabaseManager.get_sync_database()
    return db[collection_name]


async def create_indexes():
    """Create database indexes for optimal performance."""
    db = DatabaseManager.get_database()
    
    # Clients indexes
    await db[Collections.CLIENTS].create_index([("email", 1)], unique=True)
    await db[Collections.CLIENTS].create_index([("phone", 1)])
    await db[Collections.CLIENTS].create_index([("name", "text"), ("email", "text")])
    await db[Collections.CLIENTS].create_index([("status", 1)])
    
    # Orders indexes
    await db[Collections.ORDERS].create_index([("client_id", 1)])
    await db[Collections.ORDERS].create_index([("status", 1)])
    await db[Collections.ORDERS].create_index([("created_date", -1)])
    await db[Collections.ORDERS].create_index([("service_type", 1), ("service_id", 1)])
    
    # Payments indexes
    await db[Collections.PAYMENTS].create_index([("order_id", 1)])
    await db[Collections.PAYMENTS].create_index([("status", 1)])
    await db[Collections.PAYMENTS].create_index([("payment_date", -1)])
    
    # Courses indexes
    await db[Collections.COURSES].create_index([("name", "text"), ("description", "text")])
    await db[Collections.COURSES].create_index([("instructor", 1)])
    await db[Collections.COURSES].create_index([("category", 1)])
    await db[Collections.COURSES].create_index([("is_active", 1)])
    
    # Classes indexes
    await db[Collections.CLASSES].create_index([("course_id", 1)])
    await db[Collections.CLASSES].create_index([("instructor", 1)])
    await db[Collections.CLASSES].create_index([("schedule", 1)])
    await db[Collections.CLASSES].create_index([("is_cancelled", 1)])
    
    # Attendance indexes
    await db[Collections.ATTENDANCE].create_index([("class_id", 1), ("client_id", 1)], unique=True)
    await db[Collections.ATTENDANCE].create_index([("client_id", 1)])
    await db[Collections.ATTENDANCE].create_index([("date", -1)])
    await db[Collections.ATTENDANCE].create_index([("status", 1)])
    
    logger.info("Database indexes created successfully")
