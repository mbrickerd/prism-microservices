"""
Drift detection events for the Sensor Failure Detection System.

This module defines the DriftEvent model that records detected
data drift between the reference data distribution (used for training)
and the current data distribution observed in production.
"""

from datetime import datetime
from typing import Any
from pydantic import Field

from domain.models.base import MongoBaseModel


class DriftEvent(MongoBaseModel):
    """
    Model representing a detected drift event.

    This class stores information about detected data drift events,
    which occur when the distribution of sensor data changes significantly
    from the distribution used to train the models. These events may
    trigger retraining of models or alerts to operators.

    Attributes:
        id (ObjectId): MongoDB document ID
        detection_time (datetime): When the drift was detected
        drift_score (float): Quantitative measure of drift magnitude
        reference_distribution (Dict): Statistical summary of the reference distribution
        current_distribution (Dict): Statistical summary of the current distribution
    """
    detection_time: datetime = Field(default_factory=datetime.now, description="When the drift was detected")
    drift_score: float = Field(..., description="Quantitative measure of drift magnitude")
    reference_distribution: dict[str, Any] = Field(..., description="Statistical summary of the reference distribution")
    current_distribution: dict[str, Any] = Field(..., description="Statistical summary of the current distribution")
    
    class Config:
        collection = "drift"

    def __str__(self) -> str:
        return f"Drift event at {self.detection_time} (score: {self.drift_score})"