from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import logging

from ..models.schemas import (
    CreateClientRequest, CreateOrderRequest, 
    Client, Order, Payment, Course, Class, Attendance,
    QueryRequest, QueryResponse
)
from ..models.database import get_collection, Collections
from ..tools.external_api_tool import ExternalAPITool

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "fitness-studio-api"}


# Client endpoints
@router.post("/clients", response_model=dict)
async def create_client(client_data: CreateClientRequest):
    """Create a new client via external API."""
    try:
        external_api = ExternalAPITool()
        result = external_api._run(
            "create_client",
            name=client_data.name,
            email=client_data.email,
            phone=client_data.phone,
            birthday=client_data.birthday,
            address=client_data.address,
            emergency_contact=client_data.emergency_contact,
            notes=client_data.notes
        )
        return {"message": "Client created successfully", "result": result}
    except Exception as e:
        logger.error(f"Error creating client: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clients", response_model=List[dict])
async def get_clients(
    status: Optional[str] = None,
    limit: int = 50,
    skip: int = 0
):
    """Get clients with optional filtering."""
    try:
        collection = get_collection(Collections.CLIENTS)
        
        # Build query
        query = {}
        if status:
            query["status"] = status
        
        # Execute query
        cursor = collection.find(query).skip(skip).limit(limit)
        clients = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for client in clients:
            client["_id"] = str(client["_id"])
        
        return clients
    except Exception as e:
        logger.error(f"Error fetching clients: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clients/{client_id}", response_model=dict)
async def get_client_by_id(client_id: str):
    """Get a specific client by ID."""
    try:
        from bson import ObjectId
        collection = get_collection(Collections.CLIENTS)
        
        client = await collection.find_one({"_id": ObjectId(client_id)})
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        client["_id"] = str(client["_id"])
        return client
    except Exception as e:
        logger.error(f"Error fetching client: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Order endpoints
@router.post("/orders", response_model=dict)
async def create_order(order_data: CreateOrderRequest):
    """Create a new order via external API."""
    try:
        external_api = ExternalAPITool()
        result = external_api._run(
            "create_order",
            client_email=order_data.client_email,
            service_type=order_data.service_type,
            service_name=order_data.service_name,
            amount=order_data.amount,
            notes=order_data.notes
        )
        return {"message": "Order created successfully", "result": result}
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders", response_model=List[dict])
async def get_orders(
    client_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    skip: int = 0
):
    """Get orders with optional filtering."""
    try:
        from bson import ObjectId
        collection = get_collection(Collections.ORDERS)
        
        # Build query
        query = {}
        if client_id:
            query["client_id"] = ObjectId(client_id)
        if status:
            query["status"] = status
        
        # Execute query
        cursor = collection.find(query).sort("created_date", -1).skip(skip).limit(limit)
        orders = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for order in orders:
            order["_id"] = str(order["_id"])
            order["client_id"] = str(order["client_id"])
            if "service_id" in order:
                order["service_id"] = str(order["service_id"])
        
        return orders
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Course endpoints
@router.get("/courses", response_model=List[dict])
async def get_courses(
    category: Optional[str] = None,
    instructor: Optional[str] = None,
    active_only: bool = True,
    limit: int = 50,
    skip: int = 0
):
    """Get courses with optional filtering."""
    try:
        collection = get_collection(Collections.COURSES)
        
        # Build query
        query = {}
        if category:
            query["category"] = category
        if instructor:
            query["instructor"] = instructor
        if active_only:
            query["is_active"] = True
        
        # Execute query
        cursor = collection.find(query).skip(skip).limit(limit)
        courses = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for course in courses:
            course["_id"] = str(course["_id"])
        
        return courses
    except Exception as e:
        logger.error(f"Error fetching courses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Class endpoints
@router.get("/classes", response_model=List[dict])
async def get_classes(
    course_id: Optional[str] = None,
    instructor: Optional[str] = None,
    upcoming_only: bool = True,
    limit: int = 50,
    skip: int = 0
):
    """Get classes with optional filtering."""
    try:
        from bson import ObjectId
        from datetime import datetime
        collection = get_collection(Collections.CLASSES)
        
        # Build query
        query = {}
        if course_id:
            query["course_id"] = ObjectId(course_id)
        if instructor:
            query["instructor"] = instructor
        if upcoming_only:
            query["schedule"] = {"$gte": datetime.utcnow()}
            query["is_cancelled"] = False
        
        # Execute query
        cursor = collection.find(query).sort("schedule", 1).skip(skip).limit(limit)
        classes = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string and format dates
        for class_item in classes:
            class_item["_id"] = str(class_item["_id"])
            class_item["course_id"] = str(class_item["course_id"])
        
        return classes
    except Exception as e:
        logger.error(f"Error fetching classes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Analytics endpoints for dashboard
@router.get("/analytics/revenue", response_model=dict)
async def get_revenue_metrics():
    """Get revenue analytics."""
    try:
        from datetime import datetime, timedelta
        orders_collection = get_collection(Collections.ORDERS)
        payments_collection = get_collection(Collections.PAYMENTS)
        
        # Current month revenue
        current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        total_revenue_pipeline = [
            {"$match": {"status": "paid"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        
        monthly_revenue_pipeline = [
            {"$match": {
                "status": "paid",
                "paid_date": {"$gte": current_month_start}
            }},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        
        outstanding_pipeline = [
            {"$match": {"status": "pending"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        
        total_revenue = await orders_collection.aggregate(total_revenue_pipeline).to_list(1)
        monthly_revenue = await orders_collection.aggregate(monthly_revenue_pipeline).to_list(1)
        outstanding = await orders_collection.aggregate(outstanding_pipeline).to_list(1)
        
        return {
            "total_revenue": total_revenue[0]["total"] if total_revenue else 0,
            "monthly_revenue": monthly_revenue[0]["total"] if monthly_revenue else 0,
            "outstanding_payments": outstanding[0]["total"] if outstanding else 0,
            "period": current_month_start.strftime("%Y-%m")
        }
    except Exception as e:
        logger.error(f"Error fetching revenue metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/clients", response_model=dict)
async def get_client_metrics():
    """Get client analytics."""
    try:
        from datetime import datetime, timedelta
        collection = get_collection(Collections.CLIENTS)
        
        # Client status counts
        status_pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        
        # New clients this month
        current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_clients_pipeline = [
            {"$match": {"registration_date": {"$gte": current_month_start}}},
            {"$count": "new_clients"}
        ]
        
        status_counts = await collection.aggregate(status_pipeline).to_list(10)
        new_clients = await collection.aggregate(new_clients_pipeline).to_list(1)
        
        # Format status counts
        status_dict = {item["_id"]: item["count"] for item in status_counts}
        
        return {
            "active_clients": status_dict.get("active", 0),
            "inactive_clients": status_dict.get("inactive", 0),
            "suspended_clients": status_dict.get("suspended", 0),
            "new_clients_this_month": new_clients[0]["new_clients"] if new_clients else 0,
            "total_clients": sum(status_dict.values())
        }
    except Exception as e:
        logger.error(f"Error fetching client metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
