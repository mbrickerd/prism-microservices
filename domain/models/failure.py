"""
Machine failure representation for the Sensor Failure Detection System.

This module defines the Failure model that represents episodes of
failures detected on machines based on sensor readings.
"""

from datetime import datetime
from typing import Optional
from pydantic import Field

from domain.models.base import MongoBaseModel, PyObjectId


class Failure(MongoBaseModel):
    """
    Model representing a machine failure.

    This class represents a period during which a machine was experiencing
    a failure. A failure is characterized by a start time and, if resolved,
    an end time. Active failures are those that have not yet been resolved.

    Attributes:
        id (ObjectId): MongoDB document ID
        start_time (datetime): When the failure was first detected
        end_time (datetime, optional): When the failure was resolved, or None if still active
        is_active (bool): Whether this failure is currently ongoing
        machine_id (ObjectId): Reference to the machine experiencing the failure
    """
    start_time: datetime = Field(..., description="When the failure was first detected")
    end_time: Optional[datetime] = Field(None, description="When the failure was resolved, or None if still active")
    is_active: bool = Field(default=True, description="Whether this failure is currently ongoing")
    machine_id: PyObjectId = Field(..., description="Reference to the machine experiencing the failure")
    
    class Config:
        collection = "failures"

    def __str__(self) -> str:
        return f"Failure on {self.id} from {self.start_time}"