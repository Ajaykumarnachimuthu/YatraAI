"""
Authentication & User Pydantic Schemas
"""

from typing import Optional, Dict
from pydantic import BaseModel, EmailStr, Field


class TravelDNASchema(BaseModel):
    cost_sensitivity: float = Field(default=0.50, ge=0.0, le=1.0, description="Price elasticity & budget sensitivity")
    time_sensitivity: float = Field(default=0.50, ge=0.0, le=1.0, description="Disutility of travel hours")
    reliability_sensitivity: float = Field(default=0.50, ge=0.0, le=1.0, description="Aversion to delay variance")
    comfort_preference: float = Field(default=0.50, ge=0.0, le=1.0, description="Valuation of premium cabins/berths")
    transfer_tolerance: float = Field(default=0.50, ge=0.0, le=1.0, description="Tolerance for layovers/stops")
    departure_time_flexibility: float = Field(default=0.50, ge=0.0, le=1.0, description="Willingness to travel off-peak")
    sustainability_preference: float = Field(default=0.50, ge=0.0, le=1.0, description="Aversion to carbon emissions")


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password (at least 6 characters)")
    full_name: Optional[str] = None
    travel_dna: Optional[TravelDNASchema] = None


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    travel_dna: Optional[Dict[str, float]] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UpdateDNARequest(BaseModel):
    travel_dna: TravelDNASchema

