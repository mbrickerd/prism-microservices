"""
Utility functions for the Sensor Failure Detection System.

This package contains database connection utilities, CRUD operations,
and helper functions for working with MongoDB/CosmosDB.
"""

from .db import (
    init_db,
    get_document_by_id,
    get_machine_readings,
    get_machine_failures,
    get_failure_readings,
    get_reading_predictions,
    get_active_failures,
    get_readings_in_timerange
)

from .crud import (
    create_document,
    update_document,
    delete_document,
    get_documents,
    create_machine,
    update_machine_last_seen,
    create_sensor_reading,
    create_failure,
    resolve_failure,
    create_prediction,
    create_cluster_model,
    create_drift_event,
    create_model_version,
    mark_model_version_processed
)

__all__ = [
    # Database connection and relationships
    "init_db",
    "get_document_by_id",
    "get_machine_readings",
    "get_machine_failures",
    "get_failure_readings",
    "get_reading_predictions",
    "get_active_failures",
    "get_readings_in_timerange",
    
    # CRUD operations
    "create_document",
    "update_document",
    "delete_document",
    "get_documents",
    
    # Model-specific operations
    "create_machine",
    "update_machine_last_seen",
    "create_sensor_reading",
    "create_failure",
    "resolve_failure",
    "create_prediction",
    "create_cluster_model",
    "create_drift_event",
    "create_model_version",
    "mark_model_version_processed"
]