"""
Machine entity representation for the Sensor Failure Detection System.

This module defines the Machine model that represents physical machines
being monitored by the system.
"""

from datetime import datetime
from pydantic import Field

from domain.models.base import MongoBaseModel


class Machine(MongoBaseModel):
    """
    Model representing a machine.

    This class represents a physical machine that is being monitored by the
    system. Each machine is identified by a unique machine_id and has
    timestamps tracking when it was first seen and last seen by the system.

    Attributes:
        id (ObjectId): MongoDB document ID
        machine_id (str): Unique external identifier for the machine
        first_seen (datetime): When this machine was first registered in the system
        last_seen (datetime): When this machine was last active
    """
    machine_id: str = Field(..., description="Unique external identifier for the machine")
    first_seen: datetime = Field(default_factory=datetime.now, description="When this machine was first registered in the system")
    last_seen: datetime = Field(default_factory=datetime.now, description="When this machine was last active")
    
    class Config:
        collection = "machines"

    def __str__(self) -> str:
        return f"Machine {self.machine_id}"