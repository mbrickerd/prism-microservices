"""
Database utility functions for MongoDB/CosmosDB connections and relationship helpers.

This module provides utility functions for initializing database connections
and retrieving related documents using reference-based relationships.
"""

from typing import Any, Type, TypeVar
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING, DESCENDING
from bson import ObjectId

from domain.models.base import MongoBaseModel
from domain.models import (
    Machine, 
    Failure, 
    SensorReading, 
    SensorPrediction, 
    Cluster, 
    DriftEvent,
    ModelVersion
)

T = TypeVar('T', bound=MongoBaseModel)


async def init_db(connection_string: str, db_name: str = "sensors") -> AsyncIOMotorClient:
    """
    Initialize the MongoDB connection and create indexes.
    
    This function establishes a connection to the MongoDB database using
    the provided connection string and creates necessary indexes for
    efficient querying.

    Args:
        connection_string (str): MongoDB connection string for Azure CosmosDB
        db_name (str): Database name to use. Defaults to "sensors"
        
    Returns:
        AsyncIOMotorClient: MongoDB client instance
        
    Raises:
        ConnectionError: If the database connection cannot be established
    """
    client = AsyncIOMotorClient(connection_string)
    db = client[db_name]
    
    # Create indexes for efficient querying
    await db[Machine.Config.collection].create_indexes([
        IndexModel([("machine_id", ASCENDING)], unique=True),
        IndexModel([("last_seen", DESCENDING)])
    ])
    
    await db[Failure.Config.collection].create_indexes([
        IndexModel([("machine_id", ASCENDING)]),
        IndexModel([("start_time", DESCENDING)]),
        IndexModel([("is_active", ASCENDING)])
    ])
    
    await db[SensorReading.Config.collection].create_indexes([
        IndexModel([("machine_id", ASCENDING)]),
        IndexModel([("timestamp", DESCENDING)]),
        IndexModel([("failure_id", ASCENDING)])
    ])
    
    await db[SensorPrediction.Config.collection].create_indexes([
        IndexModel([("reading_id", ASCENDING)]),
        IndexModel([("prediction_time", DESCENDING)]),
        IndexModel([("reading_id", ASCENDING), ("model_version", ASCENDING)], unique=True)
    ])
    
    await db[Cluster.Config.collection].create_indexes([
        IndexModel([("mlflow_run_id", ASCENDING)], unique=True),
        IndexModel([("created_at", DESCENDING)]),
        IndexModel([("is_active", ASCENDING)])
    ])
    
    await db[DriftEvent.Config.collection].create_indexes([
        IndexModel([("detection_time", DESCENDING)])
    ])
    
    await db[ModelVersion.Config.collection].create_indexes([
        IndexModel([("version", ASCENDING)]),
        IndexModel([("created_at", DESCENDING)]),
        IndexModel([("is_processed", ASCENDING)])
    ])
    
    return client


async def get_document_by_id(
    db: AsyncIOMotorClient, 
    collection: str, 
    doc_id: str | ObjectId, 
    model_class: Type[T]
) -> T | None:
    """
    Get a document by its ID and convert it to a specific model class
    
    Args:
        db: MongoDB database connection
        collection: Collection name
        doc_id: Document ID (can be string or ObjectId)
        model_class: Pydantic model class to convert the document to
        
    Returns:
        Document as specified model class or None if not found
    """
    if isinstance(doc_id, str) and ObjectId.is_valid(doc_id):
        doc_id = ObjectId(doc_id)
    
    doc = await db[collection].find_one({"_id": doc_id})
    if doc:
        return model_class(**doc)
    return None


async def get_machine_readings(db: AsyncIOMotorClient, machine_id: str | ObjectId) -> list[SensorReading]:
    """
    Get all readings for a specific machine
    
    Args:
        db: MongoDB database connection
        machine_id: ID of the machine
        
    Returns:
        List of sensor readings for the machine, sorted by timestamp (newest first)
    """
    if isinstance(machine_id, str) and ObjectId.is_valid(machine_id):
        machine_id = ObjectId(machine_id)
    
    cursor = db[SensorReading.Config.collection].find({"machine_id": machine_id}).sort("timestamp", DESCENDING)
    readings = [SensorReading(**doc) for doc in await cursor.to_list(length=None)]
    return readings


async def get_machine_failures(db: AsyncIOMotorClient, machine_id: str | ObjectId) -> list[Failure]:
    """
    Get all failures for a specific machine
    
    Args:
        db: MongoDB database connection
        machine_id: ID of the machine
        
    Returns:
        List of failures for the machine, sorted by start_time (newest first)
    """
    if isinstance(machine_id, str) and ObjectId.is_valid(machine_id):
        machine_id = ObjectId(machine_id)
    
    cursor = db[Failure.Config.collection].find({"machine_id": machine_id}).sort("start_time", DESCENDING)
    failures = [Failure(**doc) for doc in await cursor.to_list(length=None)]
    return failures


async def get_failure_readings(db: AsyncIOMotorClient, failure_id: str | ObjectId) -> list[SensorReading]:
    """
    Get all readings associated with a specific failure
    
    Args:
        db: MongoDB database connection
        failure_id: ID of the failure
        
    Returns:
        List of sensor readings for the failure, sorted by timestamp (newest first)
    """
    if isinstance(failure_id, str) and ObjectId.is_valid(failure_id):
        failure_id = ObjectId(failure_id)
    
    cursor = db[SensorReading.Config.collection].find({"failure_id": failure_id}).sort("timestamp", DESCENDING)
    readings = [SensorReading(**doc) for doc in await cursor.to_list(length=None)]
    return readings


async def get_reading_predictions(db: AsyncIOMotorClient, reading_id: str | ObjectId) -> list[SensorPrediction]:
    """
    Get all predictions for a specific reading
    
    Args:
        db: MongoDB database connection
        reading_id: ID of the reading
        
    Returns:
        List of predictions for the reading
    """
    if isinstance(reading_id, str) and ObjectId.is_valid(reading_id):
        reading_id = ObjectId(reading_id)
    
    cursor = db[SensorPrediction.Config.collection].find({"reading_id": reading_id})
    predictions = [SensorPrediction(**doc) for doc in await cursor.to_list(length=None)]
    return predictions


# Advanced querying functions
async def get_active_failures(db: AsyncIOMotorClient) -> list[Failure]:
    """
    Get all currently active failures across all machines
    
    Args:
        db: MongoDB database connection
        
    Returns:
        List of active failures, sorted by start_time (newest first)
    """
    cursor = db[Failure.Config.collection].find({"is_active": True}).sort("start_time", DESCENDING)
    failures = [Failure(**doc) for doc in await cursor.to_list(length=None)]
    return failures


async def get_readings_in_timerange(
    db: AsyncIOMotorClient, 
    machine_id: str | ObjectId, 
    start_time: Any, 
    end_time: Any
) -> list[SensorReading]:
    """
    Get readings for a machine within a specific time range
    
    Args:
        db: MongoDB database connection
        machine_id: ID of the machine
        start_time: Start of the time range
        end_time: End of the time range
        
    Returns:
        List of readings in the specified time range, sorted by timestamp (newest first)
    """
    if isinstance(machine_id, str) and ObjectId.is_valid(machine_id):
        machine_id = ObjectId(machine_id)
    
    cursor = db[SensorReading.Config.collection].find({
        "machine_id": machine_id,
        "timestamp": {"$gte": start_time, "$lte": end_time}
    }).sort("timestamp", DESCENDING)
    
    readings = [SensorReading(**doc) for doc in await cursor.to_list(length=None)]
    return readings