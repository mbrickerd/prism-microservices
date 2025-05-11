"""
Sensor reading representation for the Sensor Failure Detection System.

This module defines the SensorReading model that stores sensor measurements
collected from machines, including their timestamp and values.
"""

from datetime import datetime
from pydantic import Field

from domain.models.base import MongoBaseModel, PyObjectId


class SensorReading(MongoBaseModel):
    """
    Model representing a sensor reading.

    This class stores sensor measurements collected from machines. Each reading
    includes a timestamp, the sensor values as a JSON object, and references
    to the source machine and any active failure at the time of the reading.

    Attributes:
        id (ObjectId): MongoDB document ID
        timestamp (datetime): When the reading was taken
        values (Dict[str, float]): Sensor measurements
        machine_id (ObjectId): Reference to the machine that produced this reading
        failure_id (ObjectId, optional): Reference to an active failure, if any
    """
    timestamp: datetime = Field(..., description="When the reading was taken")
    values: dict[str, float] = Field(..., description="Sensor measurements")
    machine_id: PyObjectId = Field(..., description="Reference to the machine that produced this reading")
    failure_id: PyObjectId | None = Field(None, description="Reference to an active failure, if any")
    
    class Config:
        collection = "readings"

    def __str__(self) -> str:
        return f"Reading for {self.id} at {self.timestamp}"