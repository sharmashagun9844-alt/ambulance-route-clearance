from pydantic import BaseModel, Field
from typing import List, Optional

# ─────────────────────────────────────────
#  MODELS — typed contracts for OpenEnv
#  Action → what AI agent sends
#  Observation → what AI agent receives back
#  State → current environment status
# ─────────────────────────────────────────

class Signal(BaseModel):
    id: int
    position: int
    status: str        # "red" or "green"
    traffic: str       # "light", "moderate", "heavy"

class AmbulanceAction(BaseModel):
    """What the AI agent does each step"""
    signal_id: int = Field(..., description="ID of the traffic signal to control")
    new_status: str = Field("green", description="Set signal to 'green' to clear or 'red' to block")
    reroute: bool = Field(False, description="True if agent wants to reroute around blocked road")

class AmbulanceObservation(BaseModel):
    """What the AI agent sees after each step"""
    ambulance_position: object          # int for task 1&2, list for task 3
    hospital_position: int
    signals: List[Signal]
    blocked_roads: List[int]
    time_elapsed: int
    ambulances: int
    reward: float = 0.0
    done: bool = False
    message: str = ""

class AmbulanceState(BaseModel):
    """Full current state of environment"""
    task_id: int
    step_count: int
    ambulance_reached: bool
    ambulance_position: object
    hospital_position: int
    signals: List[Signal]
    blocked_roads: List[int]
    time_elapsed: int
