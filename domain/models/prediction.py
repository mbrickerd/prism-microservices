"""
ML prediction representation for the Sensor Failure Detection System.

This module defines the SensorPrediction model that stores the results
of machine learning predictions made on sensor readings.
"""

from datetime import datetime
from pydantic import Field

from domain.models.base import MongoBaseModel, PyObjectId


class SensorPrediction(MongoBaseModel):
    """
    Model representing a prediction for a sensor reading.

    This class stores the results of machine learning predictions made
    on sensor readings. Each prediction associates a reading with a
    specific cluster identified by the model and includes metadata
    about the model version used and confidence scores.

    Attributes:
        id (ObjectId): MongoDB document ID
        cluster_id (int): Identifier of the predicted cluster
        model_version (str): Version of the model used for prediction
        confidence_score (float, optional): Confidence level of the prediction
        prediction_time (datetime): When the prediction was made
        mlflow_run_id (str, optional): MLflow run ID of the model used
        model_name (str): Name of the machine learning model
        reading_id (ObjectId): Reference to the sensor reading being predicted
    """
    cluster_id: int = Field(..., description="Identifier of the predicted cluster")
    model_version: str = Field(..., description="Version of the model used for prediction")
    confidence_score: float | None = Field(None, description="Confidence level of the prediction")
    prediction_time: datetime = Field(default_factory=datetime.now, description="When the prediction was made")
    mlflow_run_id: str | None = Field(None, description="MLflow run ID of the model used")
    model_name: str = Field("sensor_failure_clustering", description="Name of the machine learning model")
    reading_id: PyObjectId = Field(..., description="Reference to the sensor reading being predicted")
    
    class Config:
        collection = "predictions"

    def __str__(self) -> str:
        return f"Prediction for reading {self.reading_id}: cluster {self.cluster_id}"