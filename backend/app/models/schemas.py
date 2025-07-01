from pydantic import BaseModel, Field, EmailStr, ConfigDict
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: core_schema.CoreSchema, handler
    ) -> JsonSchemaValue:
        return {"type": "string"}


class ClientStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


# Client Models
class Client(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$")
    status: ClientStatus = ClientStatus.ACTIVE
    enrolled_services: List[str] = Field(default_factory=list)
    registration_date: datetime = Field(default_factory=datetime.utcnow)
    birthday: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    address: Optional[str] = None
    emergency_contact: Optional[Dict[str, str]] = None
    notes: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )


# Order Models
class Order(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    client_id: PyObjectId
    service_type: str  # "course" or "class"
    service_id: PyObjectId
    service_name: str
    amount: float = Field(..., gt=0)
    status: OrderStatus = OrderStatus.PENDING
    created_date: datetime = Field(default_factory=datetime.utcnow)
    due_date: Optional[datetime] = None
    paid_date: Optional[datetime] = None
    discount_applied: Optional[float] = 0.0
    tax_amount: Optional[float] = 0.0
    notes: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )


# Payment Models
class Payment(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    order_id: PyObjectId
    amount: float = Field(..., gt=0)
    payment_date: datetime = Field(default_factory=datetime.utcnow)
    method: str  # "cash", "card", "online", "bank_transfer"
    status: PaymentStatus = PaymentStatus.PENDING
    transaction_id: Optional[str] = None
    gateway_response: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )


# Course Models
class Course(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., min_length=1, max_length=100)
    instructor: str = Field(..., min_length=1, max_length=100)
    description: str
    duration_weeks: int = Field(..., gt=0)
    capacity: int = Field(..., gt=0)
    enrollment_count: int = Field(default=0, ge=0)
    completion_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    price: float = Field(..., gt=0)
    category: str
    difficulty_level: str  # "beginner", "intermediate", "advanced"
    prerequisites: List[str] = Field(default_factory=list)
    is_active: bool = True
    created_date: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )


# Class Models
class Class(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    course_id: PyObjectId
    course_name: str
    instructor: str
    schedule: datetime
    duration_minutes: int = Field(..., gt=0)
    capacity: int = Field(..., gt=0)
    enrolled_count: int = Field(default=0, ge=0)
    room: Optional[str] = None
    equipment_needed: List[str] = Field(default_factory=list)
    is_cancelled: bool = False
    cancellation_reason: Optional[str] = None
    notes: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )


# Attendance Models
class Attendance(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    class_id: PyObjectId
    client_id: PyObjectId
    date: datetime = Field(default_factory=datetime.utcnow)
    status: AttendanceStatus = AttendanceStatus.PRESENT
    checked_in_time: Optional[datetime] = None
    checked_out_time: Optional[datetime] = None
    notes: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )


# API Request/Response Models
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    language: Optional[str] = "en"
    context: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    response: str
    data: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None
    language: Optional[str] = "en"


class ErrorResponse(BaseModel):
    error: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CreateClientRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$")
    birthday: Optional[datetime] = None
    address: Optional[str] = None
    emergency_contact: Optional[Dict[str, str]] = None
    notes: Optional[str] = None


class CreateOrderRequest(BaseModel):
    client_email: str
    service_type: str  # "course" or "class"
    service_name: str
    amount: Optional[float] = None  # If not provided, will be fetched from service
    notes: Optional[str] = None
