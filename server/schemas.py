from ninja import Schema
from datetime import datetime
from pydantic import Field


class LocationSchema(Schema):
    latitude: float
    longitude: float


class SafeguardReportOut(Schema):
    id: int
    machine_serial: str = "844585" 
    report_datetime: datetime = Field(..., alias="report_datetime")
    engine_off_timestamp: datetime
    is_safe: bool
    location: LocationSchema
    distance_to_road_m: float
    is_active: bool

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat().replace("+00:00", "Z")
        }


class ProcessingResponseSchema(Schema):
    message: str


class UpdateActiveSchema(Schema):
    is_active: bool
