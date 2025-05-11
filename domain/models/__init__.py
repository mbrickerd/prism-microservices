"""
Domain models for the Sensor Failure Detection System.

This package provides a centralised definition of all database entities used
throughout the Sensor Failure Detection System, ensuring consistency across
microservices. It leverages Pydantic for data validation and PyMongo/Motor for 
MongoDB/CosmosDB interaction.

This package serves as a single source of truth for data models across all
microservices in the system, eliminating duplication and enforcing consistency.
"""

from .cluster import Cluster
from .drift import DriftEvent
from .failure import Failure
from .machine import Machine
from .prediction import SensorPrediction
from .reading import SensorReading
from .version import ModelVersion

__all__ = [
    "Machine",
    "SensorReading",
    "Failure",
    "Cluster",
    "SensorPrediction",
    "DriftEvent",
    "ModelVersion",
]