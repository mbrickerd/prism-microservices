"""
Base model for MongoDB documents in the Sensor Failure Detection System.

This module defines the base model class for all MongoDB documents,
including handling of ObjectId fields and common configuration.
"""

from datetime import datetime
from typing import Any, Callable, Generator, Type
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    """
    Custom type for handling MongoDB ObjectId, making it compatible with Pydantic.
    """
    @classmethod
    def __get_validators__(cls: Type[ObjectId]) -> Generator[Callable, None, None]:
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls: Type[ObjectId], field_schema: dict[str, Any]) -> None:
        field_schema.update(type="string")


class MongoBaseModel(BaseModel):
    """
    Base model for all MongoDB documents.
    
    Provides common functionality for MongoDB document models,
    such as handling ObjectId fields and configuring JSON serialization.
    
    Attributes:
        id (ObjectId, optional): MongoDB document ID
    """
    id: PyObjectId | None = Field(default_factory=PyObjectId, alias="_id")
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }