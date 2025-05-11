"""
Clustering model representation for the Sensor Failure Detection System.

This module defines the Cluster model that stores information about
trained clustering models, including their performance metrics, parameters,
and MLflow tracking information.
"""

from datetime import datetime
from typing import Any
from pydantic import Field

from domain.models.base import MongoBaseModel


class Cluster(MongoBaseModel):
    """
    Model representing a trained clustering model.

    This class stores information about clustering models that have been
    trained on sensor data. It includes references to the MLflow run where
    the model is tracked, performance metrics such as silhouette score,
    and the profiles of each identified cluster.

    Attributes:
        id (ObjectId): MongoDB document ID
        mlflow_run_id (str): Unique identifier for the MLflow run where this model is tracked
        mlflow_model_version (int): MLflow model registry version number
        created_at (datetime): Timestamp when this record was created
        is_active (bool): Whether this is the currently active clustering model
        n_clusters (int): Number of clusters in this model
        silhouette_score (float): Clustering quality metric
        cluster_profiles (Dict): JSON representation of the cluster centroids and characteristics
    """
    mlflow_run_id: str = Field(..., description="Unique identifier for the MLflow run where this model is tracked")
    mlflow_model_version: int = Field(..., description="MLflow model registry version number")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp when this record was created")
    is_active: bool = Field(default=False, description="Whether this is the currently active clustering model")
    n_clusters: int = Field(..., description="Number of clusters in this model")
    silhouette_score: float = Field(..., description="Clustering quality metric")
    cluster_profiles: dict[str, Any] = Field(..., description="JSON representation of the cluster centroids and characteristics")
    
    class Config:
        collection = "clusters"

    def __str__(self) -> str:
        return f"Cluster {self.id} (Run: {self.mlflow_run_id})"