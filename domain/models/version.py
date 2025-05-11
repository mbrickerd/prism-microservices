"""
Model version tracking for the Sensor Failure Detection System.

This module defines the ModelVersion model that tracks when new versions
of machine learning models become available for use in the system.
"""

from datetime import datetime
from pydantic import Field

from domain.models.base import MongoBaseModel


class ModelVersion(MongoBaseModel):
    """
    Tracks when new model versions are available.

    This class stores information about new versions of machine learning models
    that become available in the model registry. It helps the prediction service
    know when to update the models it uses for making predictions.

    Attributes:
        id (ObjectId): MongoDB document ID
        version (str): Version identifier of the model
        run_id (str): MLflow run ID where the model is stored
        created_at (datetime): When this model version was registered
        is_processed (bool): Whether this version has been processed by the predictor
    """
    version: str = Field(..., description="Version identifier of the model")
    run_id: str = Field(..., description="MLflow run ID where the model is stored")
    created_at: datetime = Field(default_factory=datetime.now, description="When this model version was registered")
    is_processed: bool = Field(default=False, description="Whether this version has been processed by the predictor")
    
    class Config:
        collection = "versions"

    def __str__(self) -> str:
        return f"Model version {self.version} (Run: {self.run_id})"