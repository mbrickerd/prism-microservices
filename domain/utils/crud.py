"""
CRUD operations for MongoDB/CosmosDB models.

This module provides generic create, read, update, and delete functionality
for MongoDB documents, as well as specific helpers for the sensor models.
"""

from typing import Any, Type, TypeVar
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
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


async def create_document(
    db: AsyncIOMotorDatabase, 
    document: T,
) -> ObjectId:
    """
    Create a new document in the database
    
    Args:
        db: MongoDB database
        document: Document to create (Pydantic model instance)
        
    Returns:
        ID of the created document
    """
    collection = document.__class__.Config.collection
    result = await db[collection].insert_one(document.dict(by_alias=True, exclude_none=True))
    return result.inserted_id


async def update_document(
    db: AsyncIOMotorDatabase, 
    collection: str, 
    doc_id: str | ObjectId, 
    update_data: dict[str, Any]
) -> bool:
    """
    Update an existing document
    
    Args:
        db: MongoDB database
        collection: Collection name
        doc_id: Document ID
        update_data: Dictionary of fields to update
        
    Returns:
        True if document was found and updated, False otherwise
    """
    if isinstance(doc_id, str) and ObjectId.is_valid(doc_id):
        doc_id = ObjectId(doc_id)
    
    result = await db[collection].update_one(
        {"_id": doc_id}, 
        {"$set": update_data}
    )
    
    return result.matched_count > 0


async def delete_document(
    db: AsyncIOMotorDatabase, 
    collection: str, 
    doc_id: str | ObjectId,
) -> bool:
    """
    Delete a document from the database
    
    Args:
        db: MongoDB database
        collection: Collection name
        doc_id: Document ID
        
    Returns:
        True if document was found and deleted, False otherwise
    """
    if isinstance(doc_id, str) and ObjectId.is_valid(doc_id):
        doc_id = ObjectId(doc_id)
    
    result = await db[collection].delete_one({"_id": doc_id})
    return result.deleted_count > 0


async def get_documents(
    db: AsyncIOMotorDatabase, 
    collection: str, 
    model_class: Type[T], 
    query: dict[str, Any] = None,
    sort_by: list[tuple] = None,
    limit: int = 0,
    skip: int = 0
) -> list[T]:
    """
    Get documents matching a query
    
    Args:
        db: MongoDB database
        collection: Collection name
        model_class: Pydantic model class to convert documents to
        query: MongoDB query (default: empty query that matches all documents)
        sort_by: List of (field, direction) tuples for sorting
        limit: Maximum number of documents to return (0 means no limit)
        skip: Number of documents to skip
        
    Returns:
        List of documents matching the query
    """
    query = query or {}
    cursor = db[collection].find(query)
    
    if sort_by:
        cursor = cursor.sort(sort_by)
    
    if skip:
        cursor = cursor.skip(skip)
    
    if limit:
        cursor = cursor.limit(limit)
    
    docs = await cursor.to_list(length=None)
    return [model_class(**doc) for doc in docs]


# Specific CRUD operations for sensor models
async def create_machine(db: AsyncIOMotorDatabase, machine_id: str) -> ObjectId:
    """
    Create a new machine
    
    Args:
        db: MongoDB database
        machine_id: External identifier for the machine
        
    Returns:
        ID of the created machine
    """
    machine = Machine(
        machine_id=machine_id, 
        first_seen=datetime.now(),
        last_seen=datetime.now()
    )
    
    return await create_document(db, machine)


async def update_machine_last_seen(
    db: AsyncIOMotorDatabase, 
    machine_id: str | ObjectId,
) -> bool:
    """
    Update the last_seen timestamp of a machine
    
    Args:
        db: MongoDB database
        machine_id: ID of the machine
        
    Returns:
        True if machine was found and updated, False otherwise
    """
    if isinstance(machine_id, str) and ObjectId.is_valid(machine_id):
        machine_id = ObjectId(machine_id)
    
    result = await db[Machine.Config.collection].update_one(
        {"_id": machine_id},
        {"$set": {"last_seen": datetime.now()}}
    )
    
    return result.matched_count > 0


async def create_sensor_reading(
    db: AsyncIOMotorDatabase, 
    machine_id: str | ObjectId, 
    values: dict[str, float],
    timestamp: datetime | None = None,
    failure_id: str | ObjectId = None
) -> ObjectId:
    """
    Create a new sensor reading
    
    Args:
        db: MongoDB database
        machine_id: ID of the machine
        values: Sensor measurements
        timestamp: When the reading was taken (defaults to current time)
        failure_id: ID of the associated failure, if any
        
    Returns:
        ID of the created reading
    """
    if isinstance(machine_id, str) and ObjectId.is_valid(machine_id):
        machine_id = ObjectId(machine_id)
    
    if isinstance(failure_id, str) and ObjectId.is_valid(failure_id):
        failure_id = ObjectId(failure_id)
    
    reading = SensorReading(
        timestamp=timestamp or datetime.now(),
        values=values,
        machine_id=machine_id,
        failure_id=failure_id
    )
    
    reading_id = await create_document(db, reading)
    
    # Update the machine's last_seen timestamp
    await update_machine_last_seen(db, machine_id)
    
    return reading_id


async def create_failure(
    db: AsyncIOMotorDatabase, 
    machine_id: str | ObjectId,
    start_time: datetime | None = None
) -> ObjectId:
    """
    Create a new failure record
    
    Args:
        db: MongoDB database
        machine_id: ID of the machine
        start_time: When the failure started (defaults to current time)
        
    Returns:
        ID of the created failure
    """
    if isinstance(machine_id, str) and ObjectId.is_valid(machine_id):
        machine_id = ObjectId(machine_id)
    
    failure = Failure(
        start_time=start_time or datetime.now(),
        is_active=True,
        machine_id=machine_id
    )
    
    return await create_document(db, failure)


async def resolve_failure(
    db: AsyncIOMotorDatabase, 
    failure_id: str | ObjectId,
    end_time: datetime | None = None
) -> bool:
    """
    Mark a failure as resolved
    
    Args:
        db: MongoDB database
        failure_id: ID of the failure
        end_time: When the failure was resolved (defaults to current time)
        
    Returns:
        True if failure was found and updated, False otherwise
    """
    if isinstance(failure_id, str) and ObjectId.is_valid(failure_id):
        failure_id = ObjectId(failure_id)
    
    result = await db[Failure.Config.collection].update_one(
        {"_id": failure_id, "is_active": True},
        {"$set": {
            "end_time": end_time or datetime.now(),
            "is_active": False
        }}
    )
    
    return result.matched_count > 0


async def create_prediction(
    db: AsyncIOMotorDatabase, 
    reading_id: str | ObjectId,
    cluster_id: int,
    model_version: str,
    confidence_score: float | None = None,
    mlflow_run_id: str | None = None,
    model_name: str = "sensor_failure_clustering"
) -> ObjectId:
    """
    Create a new prediction for a sensor reading
    
    Args:
        db: MongoDB database
        reading_id: ID of the reading
        cluster_id: ID of the predicted cluster
        model_version: Version of the model used
        confidence_score: Confidence level of the prediction
        mlflow_run_id: MLflow run ID of the model used
        model_name: Name of the machine learning model
        
    Returns:
        ID of the created prediction
    """
    if isinstance(reading_id, str) and ObjectId.is_valid(reading_id):
        reading_id = ObjectId(reading_id)
    
    prediction = SensorPrediction(
        cluster_id=cluster_id,
        model_version=model_version,
        confidence_score=confidence_score,
        prediction_time=datetime.now(),
        mlflow_run_id=mlflow_run_id,
        model_name=model_name,
        reading_id=reading_id
    )
    
    return await create_document(db, prediction)


async def create_cluster_model(
    db: AsyncIOMotorDatabase, 
    mlflow_run_id: str,
    mlflow_model_version: int,
    n_clusters: int,
    silhouette_score: float,
    cluster_profiles: dict[str, Any],
    is_active: bool = False
) -> ObjectId:
    """
    Create a new clustering model
    
    Args:
        db: MongoDB database
        mlflow_run_id: Unique identifier for the MLflow run
        mlflow_model_version: MLflow model registry version number
        n_clusters: Number of clusters in this model
        silhouette_score: Clustering quality metric
        cluster_profiles: JSON representation of the cluster centroids
        is_active: Whether this is the currently active clustering model
        
    Returns:
        ID of the created cluster model
    """
    # If this model is active, deactivate all other models
    if is_active:
        await db[Cluster.Config.collection].update_many(
            {"is_active": True},
            {"$set": {"is_active": False}}
        )
    
    cluster = Cluster(
        mlflow_run_id=mlflow_run_id,
        mlflow_model_version=mlflow_model_version,
        created_at=datetime.now(),
        is_active=is_active,
        n_clusters=n_clusters,
        silhouette_score=silhouette_score,
        cluster_profiles=cluster_profiles
    )
    
    return await create_document(db, cluster)


async def create_drift_event(
    db: AsyncIOMotorDatabase, 
    drift_score: float,
    reference_distribution: dict[str, Any],
    current_distribution: dict[str, Any]
) -> ObjectId:
    """
    Create a new drift event
    
    Args:
        db: MongoDB database
        drift_score: Quantitative measure of drift magnitude
        reference_distribution: Statistical summary of the reference distribution
        current_distribution: Statistical summary of the current distribution
        
    Returns:
        ID of the created drift event
    """
    drift = DriftEvent(
        detection_time=datetime.now(),
        drift_score=drift_score,
        reference_distribution=reference_distribution,
        current_distribution=current_distribution
    )
    
    return await create_document(db, drift)


async def create_model_version(
    db: AsyncIOMotorDatabase, 
    version: str,
    run_id: str,
    is_processed: bool = False
) -> ObjectId:
    """
    Create a new model version
    
    Args:
        db: MongoDB database
        version: Version identifier of the model
        run_id: MLflow run ID where the model is stored
        is_processed: Whether this version has been processed by the predictor
        
    Returns:
        ID of the created model version
    """
    model_version = ModelVersion(
        version=version,
        run_id=run_id,
        created_at=datetime.now(),
        is_processed=is_processed
    )
    
    return await create_document(db, model_version)


async def mark_model_version_processed(
    db: AsyncIOMotorDatabase, 
    version_id: str | ObjectId,
) -> bool:
    """
    Mark a model version as processed
    
    Args:
        db: MongoDB database
        version_id: ID of the model version
        
    Returns:
        True if model version was found and updated, False otherwise
    """
    if isinstance(version_id, str) and ObjectId.is_valid(version_id):
        version_id = ObjectId(version_id)
    
    result = await db[ModelVersion.Config.collection].update_one(
        {"_id": version_id},
        {"$set": {"is_processed": True}}
    )
    
    return result.matched_count > 0