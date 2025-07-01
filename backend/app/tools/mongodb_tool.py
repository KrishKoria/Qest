from crewai.tools import BaseTool
from typing import Optional, Dict, Any, List
import json
from datetime import datetime, timedelta
from bson import ObjectId
from pymongo.errors import PyMongoError
import logging

from ..models.database import get_sync_collection, Collections
from ..models.schemas import ClientStatus, OrderStatus, AttendanceStatus

logger = logging.getLogger(__name__)


class MongoDBTool(BaseTool):
    name: str = "MongoDB Query Tool"
    description: str = """
    A comprehensive tool for querying MongoDB collections in a fitness studio database.
    
    Capabilities:
    - Client search and management
    - Order and payment tracking
    - Course and class information
    - Attendance monitoring  
    - Business analytics and reporting
    
    Use this tool for all database queries and analytics operations.
    """

    def _run(self, query_type: str, **kwargs) -> str:
        """
        Execute MongoDB operations based on query type.
        
        Args:
            query_type: Type of operation to perform
            **kwargs: Additional parameters for the operation
        """
        try:
            # Normalize the query type to handle natural language queries from agents
            normalized_query = self._normalize_query_type(query_type)
            
            if normalized_query == "find_clients":
                return self._find_clients(**kwargs)
            elif normalized_query == "get_client_by_id":
                return self._get_client_by_id(**kwargs)
            elif normalized_query == "search_clients":
                return self._search_clients(**kwargs)
            elif normalized_query == "get_orders":
                return self._get_orders(**kwargs)
            elif normalized_query == "get_order_by_id":
                return self._get_order_by_id(**kwargs)
            elif normalized_query == "get_payments":
                return self._get_payments(**kwargs)
            elif normalized_query == "get_courses":
                return self._get_courses(**kwargs)
            elif normalized_query == "get_classes":
                return self._get_classes(**kwargs)
            elif normalized_query == "get_attendance":
                return self._get_attendance(**kwargs)
            elif normalized_query == "revenue_analytics":
                return self._revenue_analytics(**kwargs)
            elif normalized_query == "client_analytics":
                return self._client_analytics(**kwargs)
            elif normalized_query == "service_analytics":
                return self._service_analytics(**kwargs)
            elif normalized_query == "attendance_analytics":
                return self._attendance_analytics(**kwargs)
            elif normalized_query == "summary_statistics":
                return self._get_summary_statistics(**kwargs)
            else:
                return self._get_available_query_types()
                
        except Exception as e:
            logger.error(f"MongoDB operation failed: {str(e)}")
            return f"Database operation failed: {str(e)}"
    
    def _normalize_query_type(self, query_type: str) -> str:
        """Normalize natural language query types to internal query types."""
        query_lower = query_type.lower()
        
        # Client-related queries
        if any(phrase in query_lower for phrase in ["client search and management", "recent clients", "show clients", "get clients", "find clients"]):
            return "find_clients"
        elif "client" in query_lower and ("search" in query_lower or "find" in query_lower):
            return "search_clients"
        
        # Order-related queries
        elif any(phrase in query_lower for phrase in ["order and payment tracking", "recent orders", "show orders", "get orders", "find orders"]):
            return "get_orders"
        elif "order" in query_lower and ("search" in query_lower or "find" in query_lower):
            return "get_orders"
        
        # Course-related queries
        elif any(phrase in query_lower for phrase in ["course and class information", "courses", "classes"]):
            if "class" in query_lower:
                return "get_classes"
            else:
                return "get_courses"
        
        # Attendance queries
        elif any(phrase in query_lower for phrase in ["attendance monitoring", "attendance"]):
            return "get_attendance"
        
        # Analytics queries
        elif any(phrase in query_lower for phrase in ["business analytics and reporting", "revenue", "analytics", "statistics", "summary"]):
            if "revenue" in query_lower:
                return "revenue_analytics"
            elif "client" in query_lower:
                return "client_analytics"
            elif "service" in query_lower:
                return "service_analytics"
            elif "attendance" in query_lower:
                return "attendance_analytics"
            else:
                return "summary_statistics"
        
        # Default to original query type if no match found
        return query_type
    
    def _get_available_query_types(self) -> str:
        """Return available query types for agents."""
        return """Available query types:
        - Client search and management: find_clients, search_clients
        - Order and payment tracking: get_orders, get_payments
        - Course and class information: get_courses, get_classes
        - Attendance monitoring: get_attendance
        - Business analytics and reporting: revenue_analytics, client_analytics, service_analytics, summary_statistics
        
        Please use one of these query types or a natural language description that matches these categories."""

    def _find_clients(self, status: Optional[str] = None, limit: int = 50) -> str:
        """Find clients with optional status filter."""
        try:
            collection = get_sync_collection(Collections.CLIENTS)
            filter_dict = {}
            
            if status:
                filter_dict["status"] = status
                
            clients = list(collection.find(filter_dict).limit(limit))
            
            # If no clients found, return sample data for demo purposes
            if not clients:
                sample_clients = [
                    {
                        "_id": "sample001",
                        "name": "John Smith",
                        "email": "john.smith@email.com",
                        "phone": "+1-555-0101",
                        "status": "active",
                        "registration_date": "2024-01-15T09:00:00Z",
                        "membership_type": "Premium",
                        "last_activity": "2024-07-01T08:30:00Z"
                    },
                    {
                        "_id": "sample002", 
                        "name": "Sarah Johnson",
                        "email": "sarah.johnson@email.com",
                        "phone": "+1-555-0102",
                        "status": "active",
                        "registration_date": "2024-02-20T10:00:00Z",
                        "membership_type": "Basic",
                        "last_activity": "2024-06-30T18:00:00Z"
                    },
                    {
                        "_id": "sample003",
                        "name": "Mike Davis",
                        "email": "mike.davis@email.com", 
                        "phone": "+1-555-0103",
                        "status": "active",
                        "registration_date": "2024-06-25T14:00:00Z",
                        "membership_type": "Personal Training",
                        "last_activity": "2024-06-29T16:30:00Z"
                    },
                    {
                        "_id": "sample004",
                        "name": "Emily Wilson",
                        "email": "emily.wilson@email.com",
                        "phone": "+1-555-0104", 
                        "status": "active",
                        "registration_date": "2024-03-10T11:00:00Z",
                        "membership_type": "Premium",
                        "last_activity": "2024-06-28T07:45:00Z"
                    },
                    {
                        "_id": "sample005",
                        "name": "David Brown",
                        "email": "david.brown@email.com",
                        "phone": "+1-555-0105",
                        "status": "active", 
                        "registration_date": "2024-05-05T13:00:00Z",
                        "membership_type": "Basic",
                        "last_activity": "2024-06-27T19:15:00Z"
                    }
                ]
                
                return json.dumps({
                    "success": True,
                    "count": len(sample_clients),
                    "clients": sample_clients[:limit],
                    "note": "Sample data - database appears to be empty"
                }, indent=2)
            
            # Convert ObjectId to string for JSON serialization
            for client in clients:
                client["_id"] = str(client["_id"])
                if "last_activity" in client and client["last_activity"]:
                    client["last_activity"] = client["last_activity"].isoformat()
                if "registration_date" in client:
                    client["registration_date"] = client["registration_date"].isoformat()
                if "birthday" in client and client["birthday"]:
                    client["birthday"] = client["birthday"].isoformat()
            
            return json.dumps({
                "success": True,
                "count": len(clients),
                "clients": clients
            }, indent=2)
            
        except PyMongoError as e:
            return f"Database error: {str(e)}"

    def _get_client_by_id(self, client_id: str) -> str:
        """Get a specific client by ID."""
        try:
            collection = get_sync_collection(Collections.CLIENTS)
            client = collection.find_one({"_id": ObjectId(client_id)})
            
            if not client:
                return json.dumps({"success": False, "message": "Client not found"})
            
            # Convert ObjectId to string
            client["_id"] = str(client["_id"])
            if "last_activity" in client and client["last_activity"]:
                client["last_activity"] = client["last_activity"].isoformat()
            if "registration_date" in client:
                client["registration_date"] = client["registration_date"].isoformat()
            if "birthday" in client and client["birthday"]:
                client["birthday"] = client["birthday"].isoformat()
            
            return json.dumps({
                "success": True,
                "client": client
            }, indent=2)
            
        except Exception as e:
            return f"Error retrieving client: {str(e)}"

    def _search_clients(self, search_term: str, limit: int = 20) -> str:
        """Search clients by name, email, or phone."""
        try:
            collection = get_sync_collection(Collections.CLIENTS)
            
            # Create search query for name, email, or phone
            search_query = {
                "$or": [
                    {"name": {"$regex": search_term, "$options": "i"}},
                    {"email": {"$regex": search_term, "$options": "i"}},
                    {"phone": {"$regex": search_term, "$options": "i"}}
                ]
            }
            
            clients = list(collection.find(search_query).limit(limit))
            
            for client in clients:
                client["_id"] = str(client["_id"])
                if "last_activity" in client and client["last_activity"]:
                    client["last_activity"] = client["last_activity"].isoformat()
                if "registration_date" in client:
                    client["registration_date"] = client["registration_date"].isoformat()
                if "birthday" in client and client["birthday"]:
                    client["birthday"] = client["birthday"].isoformat()
            
            return json.dumps({
                "success": True,
                "search_term": search_term,
                "count": len(clients),
                "clients": clients
            }, indent=2)
            
        except Exception as e:
            return f"Client search failed: {str(e)}"

    def _get_orders(self, client_id: Optional[str] = None, status: Optional[str] = None, limit: int = 50) -> str:
        """Get orders with optional client and status filters."""
        try:
            collection = get_sync_collection(Collections.ORDERS)
            filter_dict = {}
            
            if client_id:
                filter_dict["client_id"] = ObjectId(client_id)
            if status:
                filter_dict["status"] = status
                
            orders = list(collection.find(filter_dict).sort("created_date", -1).limit(limit))
            
            # If no orders found, return sample data for demo purposes
            if not orders:
                sample_orders = [
                    {
                        "_id": "order001",
                        "client_id": "sample001",
                        "client_name": "John Smith",
                        "service_name": "Personal Training Session",
                        "total_amount": 75.00,
                        "status": "confirmed",
                        "created_date": "2024-06-30T14:30:00Z",
                        "scheduled_date": "2024-07-02T09:00:00Z"
                    },
                    {
                        "_id": "order002",
                        "client_id": "sample002", 
                        "client_name": "Sarah Johnson",
                        "service_name": "Yoga Class Package (5 sessions)",
                        "total_amount": 125.00,
                        "status": "confirmed",
                        "created_date": "2024-06-29T16:45:00Z",
                        "scheduled_date": "2024-07-01T18:00:00Z"
                    },
                    {
                        "_id": "order003",
                        "client_id": "sample003",
                        "client_name": "Mike Davis",
                        "service_name": "HIIT Training Session",
                        "total_amount": 65.00,
                        "status": "pending",
                        "created_date": "2024-06-29T11:20:00Z",
                        "scheduled_date": "2024-07-03T07:00:00Z"
                    },
                    {
                        "_id": "order004",
                        "client_id": "sample004",
                        "client_name": "Emily Wilson", 
                        "service_name": "Pilates Session",
                        "total_amount": 80.00,
                        "status": "completed",
                        "created_date": "2024-06-28T13:15:00Z",
                        "scheduled_date": "2024-06-30T10:00:00Z",
                        "completed_date": "2024-06-30T11:00:00Z"
                    },
                    {
                        "_id": "order005",
                        "client_id": "sample005",
                        "client_name": "David Brown",
                        "service_name": "Strength Training Session", 
                        "total_amount": 70.00,
                        "status": "confirmed",
                        "created_date": "2024-06-27T09:30:00Z",
                        "scheduled_date": "2024-07-01T17:30:00Z"
                    }
                ]
                
                return json.dumps({
                    "success": True,
                    "count": len(sample_orders),
                    "orders": sample_orders[:limit],
                    "note": "Sample data - database appears to be empty"
                }, indent=2)
            
            for order in orders:
                order["_id"] = str(order["_id"])
                order["client_id"] = str(order["client_id"])
                order["service_id"] = str(order["service_id"])
                order["created_date"] = order["created_date"].isoformat()
                if "due_date" in order and order["due_date"]:
                    order["due_date"] = order["due_date"].isoformat()
                if "paid_date" in order and order["paid_date"]:
                    order["paid_date"] = order["paid_date"].isoformat()
            
            return json.dumps({
                "success": True,
                "count": len(orders),
                "orders": orders
            }, indent=2)
            
        except Exception as e:
            return f"Error retrieving orders: {str(e)}"

    def _get_order_by_id(self, order_id: str) -> str:
        """Get a specific order by ID with client and payment information."""
        try:
            orders_collection = get_sync_collection(Collections.ORDERS)
            clients_collection = get_sync_collection(Collections.CLIENTS)
            payments_collection = get_sync_collection(Collections.PAYMENTS)
            
            # Get order
            order = orders_collection.find_one({"_id": ObjectId(order_id)})
            if not order:
                return json.dumps({"success": False, "message": "Order not found"})
            
            # Get client information
            client = clients_collection.find_one({"_id": order["client_id"]})
            
            # Get payment information
            payments = list(payments_collection.find({"order_id": ObjectId(order_id)}))
            
            # Format data
            order["_id"] = str(order["_id"])
            order["client_id"] = str(order["client_id"])
            order["service_id"] = str(order["service_id"])
            order["created_date"] = order["created_date"].isoformat()
            if "due_date" in order and order["due_date"]:
                order["due_date"] = order["due_date"].isoformat()
            if "paid_date" in order and order["paid_date"]:
                order["paid_date"] = order["paid_date"].isoformat()
            
            if client:
                client["_id"] = str(client["_id"])
                order["client_info"] = {
                    "name": client["name"],
                    "email": client["email"],
                    "phone": client["phone"]
                }
            
            for payment in payments:
                payment["_id"] = str(payment["_id"])
                payment["order_id"] = str(payment["order_id"])
                payment["payment_date"] = payment["payment_date"].isoformat()
            
            order["payments"] = payments
            
            return json.dumps({
                "success": True,
                "order": order
            }, indent=2)
            
        except Exception as e:
            return f"Error retrieving order details: {str(e)}"

    def _get_payments(self, order_id: Optional[str] = None, status: Optional[str] = None, limit: int = 50) -> str:
        """Get payments with optional filters."""
        try:
            collection = get_sync_collection(Collections.PAYMENTS)
            filter_dict = {}
            
            if order_id:
                filter_dict["order_id"] = ObjectId(order_id)
            if status:
                filter_dict["status"] = status
                
            payments = list(collection.find(filter_dict).sort("payment_date", -1).limit(limit))
            
            for payment in payments:
                payment["_id"] = str(payment["_id"])
                payment["order_id"] = str(payment["order_id"])
                payment["payment_date"] = payment["payment_date"].isoformat()
            
            return json.dumps({
                "success": True,
                "count": len(payments),
                "payments": payments
            }, indent=2)
            
        except Exception as e:
            return f"Error retrieving payments: {str(e)}"

    def _get_courses(self, instructor: Optional[str] = None, active_only: bool = True, limit: int = 50) -> str:
        """Get courses with optional filters."""
        try:
            collection = get_sync_collection(Collections.COURSES)
            filter_dict = {}
            
            if instructor:
                filter_dict["instructor"] = {"$regex": instructor, "$options": "i"}
            if active_only:
                filter_dict["is_active"] = True
                
            courses = list(collection.find(filter_dict).limit(limit))
            
            for course in courses:
                course["_id"] = str(course["_id"])
                course["created_date"] = course["created_date"].isoformat()
            
            return json.dumps({
                "success": True,
                "count": len(courses),
                "courses": courses
            }, indent=2)
            
        except Exception as e:
            return f"Error retrieving courses: {str(e)}"

    def _get_classes(self, course_id: Optional[str] = None, instructor: Optional[str] = None, 
                    date_from: Optional[str] = None, date_to: Optional[str] = None, limit: int = 50) -> str:
        """Get classes with optional filters."""
        try:
            collection = get_sync_collection(Collections.CLASSES)
            filter_dict = {"is_cancelled": False}  # Only show non-cancelled classes by default
            
            if course_id:
                filter_dict["course_id"] = ObjectId(course_id)
            if instructor:
                filter_dict["instructor"] = {"$regex": instructor, "$options": "i"}
            
            if date_from or date_to:
                date_filter = {}
                if date_from:
                    date_filter["$gte"] = datetime.fromisoformat(date_from)
                if date_to:
                    date_filter["$lte"] = datetime.fromisoformat(date_to)
                filter_dict["schedule"] = date_filter
                
            classes = list(collection.find(filter_dict).sort("schedule", 1).limit(limit))
            
            for class_item in classes:
                class_item["_id"] = str(class_item["_id"])
                class_item["course_id"] = str(class_item["course_id"])
                class_item["schedule"] = class_item["schedule"].isoformat()
            
            return json.dumps({
                "success": True,
                "count": len(classes),
                "classes": classes
            }, indent=2)
            
        except Exception as e:
            return f"Error retrieving classes: {str(e)}"

    def _get_attendance(self, class_id: Optional[str] = None, client_id: Optional[str] = None, 
                       status: Optional[str] = None, limit: int = 100) -> str:
        """Get attendance records with optional filters."""
        try:
            collection = get_sync_collection(Collections.ATTENDANCE)
            filter_dict = {}
            
            if class_id:
                filter_dict["class_id"] = ObjectId(class_id)
            if client_id:
                filter_dict["client_id"] = ObjectId(client_id)
            if status:
                filter_dict["status"] = status
                
            attendance_records = list(collection.find(filter_dict).sort("date", -1).limit(limit))
            
            for record in attendance_records:
                record["_id"] = str(record["_id"])
                record["class_id"] = str(record["class_id"])
                record["client_id"] = str(record["client_id"])
                record["date"] = record["date"].isoformat()
                if "checked_in_time" in record and record["checked_in_time"]:
                    record["checked_in_time"] = record["checked_in_time"].isoformat()
                if "checked_out_time" in record and record["checked_out_time"]:
                    record["checked_out_time"] = record["checked_out_time"].isoformat()
            
            return json.dumps({
                "success": True,
                "count": len(attendance_records),
                "attendance": attendance_records
            }, indent=2)
            
        except Exception as e:
            return f"Error retrieving attendance: {str(e)}"

    def _revenue_analytics(self, period: str = "month") -> str:
        """Generate revenue analytics for the specified period."""
        try:
            orders_collection = get_sync_collection(Collections.ORDERS)
            payments_collection = get_sync_collection(Collections.PAYMENTS)
            
            # Determine date range based on period
            now = datetime.utcnow()
            if period == "week":
                start_date = now - timedelta(days=7)
            elif period == "month":
                start_date = now - timedelta(days=30)
            elif period == "quarter":
                start_date = now - timedelta(days=90)
            else:
                start_date = now - timedelta(days=30)  # Default to month
            
            # Total revenue (completed payments)
            total_revenue = payments_collection.aggregate([
                {"$match": {
                    "status": "completed",
                    "payment_date": {"$gte": start_date}
                }},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ])
            total_revenue = list(total_revenue)
            total_revenue_amount = total_revenue[0]["total"] if total_revenue else 0
            
            # Outstanding payments (pending orders)
            outstanding_payments = orders_collection.aggregate([
                {"$match": {"status": "pending"}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ])
            outstanding_payments = list(outstanding_payments)
            outstanding_amount = outstanding_payments[0]["total"] if outstanding_payments else 0
            
            # Revenue by service type
            revenue_by_service = payments_collection.aggregate([
                {"$match": {
                    "status": "completed",
                    "payment_date": {"$gte": start_date}
                }},
                {"$lookup": {
                    "from": "orders",
                    "localField": "order_id",
                    "foreignField": "_id",
                    "as": "order"
                }},
                {"$unwind": "$order"},
                {"$group": {
                    "_id": "$order.service_type",
                    "total_revenue": {"$sum": "$amount"},
                    "order_count": {"$sum": 1}
                }}
            ])
            revenue_by_service = list(revenue_by_service)
            
            analytics = {
                "success": True,
                "period": period,
                "date_range": {
                    "from": start_date.isoformat(),
                    "to": now.isoformat()
                },
                "total_revenue": total_revenue_amount,
                "outstanding_payments": outstanding_amount,
                "revenue_by_service": revenue_by_service
            }
            
            return json.dumps(analytics, indent=2)
            
        except Exception as e:
            return f"Revenue analytics failed: {str(e)}"

    def _client_analytics(self) -> str:
        """Generate client analytics and insights."""
        try:
            clients_collection = get_sync_collection(Collections.CLIENTS)
            
            # Active vs inactive clients
            client_status = clients_collection.aggregate([
                {"$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }}
            ])
            client_status = list(client_status)
            
            # New clients this month
            start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            new_clients_this_month = clients_collection.count_documents({
                "registration_date": {"$gte": start_of_month}
            })
            
            # Clients with birthdays this month
            current_month = datetime.utcnow().month
            birthday_clients = clients_collection.aggregate([
                {"$match": {"birthday": {"$ne": None}}},
                {"$project": {
                    "name": 1,
                    "email": 1,
                    "birthday": 1,
                    "birthday_month": {"$month": "$birthday"}
                }},
                {"$match": {"birthday_month": current_month}}
            ])
            birthday_clients = list(birthday_clients)
            
            for client in birthday_clients:
                client["_id"] = str(client["_id"])
                client["birthday"] = client["birthday"].isoformat()
            
            # Total client count
            total_clients = clients_collection.count_documents({})
            
            analytics = {
                "success": True,
                "total_clients": total_clients,
                "client_status_breakdown": client_status,
                "new_clients_this_month": new_clients_this_month,
                "birthday_reminders": {
                    "count": len(birthday_clients),
                    "clients": birthday_clients
                }
            }
            
            return json.dumps(analytics, indent=2)
            
        except Exception as e:
            return f"Client analytics failed: {str(e)}"

    def _service_analytics(self) -> str:
        """Generate service analytics including enrollment trends and completion rates."""
        try:
            courses_collection = get_sync_collection(Collections.COURSES)
            orders_collection = get_sync_collection(Collections.ORDERS)
            
            # Top courses by enrollment
            top_courses = courses_collection.find(
                {"is_active": True}
            ).sort("enrollment_count", -1).limit(10)
            top_courses = list(top_courses)
            
            for course in top_courses:
                course["_id"] = str(course["_id"])
                course["created_date"] = course["created_date"].isoformat()
            
            # Enrollment trends (last 30 days)
            start_date = datetime.utcnow() - timedelta(days=30)
            enrollment_trends = orders_collection.aggregate([
                {"$match": {
                    "created_date": {"$gte": start_date},
                    "status": {"$in": ["paid", "pending"]}
                }},
                {"$group": {
                    "_id": {
                        "service_type": "$service_type",
                        "service_name": "$service_name"
                    },
                    "enrollment_count": {"$sum": 1},
                    "total_revenue": {"$sum": "$amount"}
                }},
                {"$sort": {"enrollment_count": -1}}
            ])
            enrollment_trends = list(enrollment_trends)
            
            # Course completion rates
            completion_stats = courses_collection.aggregate([
                {"$match": {"is_active": True}},
                {"$group": {
                    "_id": None,
                    "avg_completion_rate": {"$avg": "$completion_rate"},
                    "courses_above_80_percent": {
                        "$sum": {"$cond": [{"$gte": ["$completion_rate", 80]}, 1, 0]}
                    },
                    "total_courses": {"$sum": 1}
                }}
            ])
            completion_stats = list(completion_stats)
            completion_data = completion_stats[0] if completion_stats else {}
            
            analytics = {
                "success": True,
                "top_courses": top_courses,
                "enrollment_trends_30_days": enrollment_trends,
                "completion_statistics": completion_data
            }
            
            return json.dumps(analytics, indent=2)
            
        except Exception as e:
            return f"Service analytics failed: {str(e)}"

    def _attendance_analytics(self, course_name: Optional[str] = None) -> str:
        """Generate attendance analytics for courses and classes."""
        try:
            attendance_collection = get_sync_collection(Collections.ATTENDANCE)
            classes_collection = get_sync_collection(Collections.CLASSES)
            
            # Build match criteria
            match_criteria = []
            if course_name:
                # Find classes matching the course name
                matching_classes = classes_collection.find(
                    {"course_name": {"$regex": course_name, "$options": "i"}},
                    {"_id": 1}
                )
                class_ids = [c["_id"] for c in matching_classes]
                if class_ids:
                    match_criteria = [{"$match": {"class_id": {"$in": class_ids}}}]
                else:
                    return json.dumps({
                        "success": False,
                        "message": f"No classes found for course: {course_name}"
                    })
            
            # Attendance percentage by class
            pipeline = match_criteria + [
                {"$lookup": {
                    "from": "classes",
                    "localField": "class_id",
                    "foreignField": "_id",
                    "as": "class_info"
                }},
                {"$unwind": "$class_info"},
                {"$group": {
                    "_id": {
                        "class_id": "$class_id",
                        "course_name": "$class_info.course_name",
                        "instructor": "$class_info.instructor",
                        "schedule": "$class_info.schedule"
                    },
                    "total_registered": {"$first": "$class_info.enrolled_count"},
                    "present_count": {
                        "$sum": {"$cond": [{"$eq": ["$status", "present"]}, 1, 0]}
                    },
                    "late_count": {
                        "$sum": {"$cond": [{"$eq": ["$status", "late"]}, 1, 0]}
                    },
                    "absent_count": {
                        "$sum": {"$cond": [{"$eq": ["$status", "absent"]}, 1, 0]}
                    }
                }},
                {"$project": {
                    "course_name": "$_id.course_name",
                    "instructor": "$_id.instructor",
                    "schedule": "$_id.schedule",
                    "total_registered": 1,
                    "present_count": 1,
                    "late_count": 1,
                    "absent_count": 1,
                    "attendance_percentage": {
                        "$multiply": [
                            {"$divide": [
                                {"$add": ["$present_count", "$late_count"]}, 
                                "$total_registered"
                            ]}, 
                            100
                        ]
                    }
                }},
                {"$sort": {"schedule": -1}}
            ]
            
            attendance_stats = list(attendance_collection.aggregate(pipeline))
            
            # Format dates
            for stat in attendance_stats:
                stat["_id"] = str(stat["_id"])
                if "schedule" in stat and stat["schedule"]:
                    stat["schedule"] = stat["schedule"].isoformat()
            
            # Overall attendance summary
            if attendance_stats:
                total_classes = len(attendance_stats)
                avg_attendance = sum(s.get("attendance_percentage", 0) for s in attendance_stats) / total_classes
                high_attendance_classes = len([s for s in attendance_stats if s.get("attendance_percentage", 0) >= 80])
            else:
                total_classes = 0
                avg_attendance = 0
                high_attendance_classes = 0
            
            analytics = {
                "success": True,
                "query_course": course_name,
                "summary": {
                    "total_classes_analyzed": total_classes,
                    "average_attendance_percentage": round(avg_attendance, 2),
                    "classes_with_80_plus_attendance": high_attendance_classes
                },
                "class_details": attendance_stats
            }
            
            return json.dumps(analytics, indent=2)
            
        except Exception as e:
            return f"Attendance analytics failed: {str(e)}"

    def _get_summary_statistics(self) -> str:
        """Get overall studio statistics summary."""
        try:
            # Get collections
            clients_collection = get_sync_collection(Collections.CLIENTS)
            orders_collection = get_sync_collection(Collections.ORDERS)
            courses_collection = get_sync_collection(Collections.COURSES)
            classes_collection = get_sync_collection(Collections.CLASSES)
            
            # Count totals
            total_clients = clients_collection.count_documents({})
            active_clients = clients_collection.count_documents({"status": ClientStatus.ACTIVE})
            total_orders = orders_collection.count_documents({})
            active_orders = orders_collection.count_documents({"status": {"$in": [OrderStatus.CONFIRMED, OrderStatus.IN_PROGRESS]}})
            total_courses = courses_collection.count_documents({"active": True})
            
            # If database is empty, return sample statistics
            if total_clients == 0 and total_orders == 0:
                sample_summary = {
                    "success": True,
                    "generated_at": datetime.now().isoformat(),
                    "studio_overview": {
                        "total_clients": 25,
                        "active_clients": 23,
                        "new_clients_this_month": 5,
                        "client_retention_rate": 92.0
                    },
                    "orders_and_revenue": {
                        "total_orders": 48,
                        "active_orders": 12,
                        "orders_this_month": 18,
                        "monthly_revenue": 3450.0,
                        "average_order_value": 191.67
                    },
                    "courses_and_classes": {
                        "available_courses": 8,
                        "upcoming_classes": 15,
                        "most_popular_course": "HIIT Training"
                    },
                    "business_metrics": {
                        "monthly_growth_rate": "+12% compared to last month",
                        "capacity_utilization": "78% average class capacity",
                        "customer_satisfaction": "4.8/5.0 average rating"
                    },
                    "note": "Sample data - database appears to be empty"
                }
                
                return json.dumps(sample_summary, indent=2)
            
            # Get recent activity
            recent_date = datetime.now() - timedelta(days=30)
            new_clients_this_month = clients_collection.count_documents({
                "registration_date": {"$gte": recent_date}
            })
            
            orders_this_month = orders_collection.count_documents({
                "created_at": {"$gte": recent_date}
            })
            
            # Calculate revenue (sum of completed orders this month)
            revenue_pipeline = [
                {
                    "$match": {
                        "status": OrderStatus.COMPLETED,
                        "created_at": {"$gte": recent_date}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_revenue": {"$sum": "$total_amount"}
                    }
                }
            ]
            
            revenue_result = list(orders_collection.aggregate(revenue_pipeline))
            monthly_revenue = revenue_result[0]["total_revenue"] if revenue_result else 0
            
            # Get upcoming classes count
            upcoming_classes = classes_collection.count_documents({
                "start_time": {"$gte": datetime.now()}
            })
            
            # Get most popular course
            popular_course_pipeline = [
                {"$group": {"_id": "$course_id", "order_count": {"$sum": 1}}},
                {"$sort": {"order_count": -1}},
                {"$limit": 1}
            ]
            
            popular_course_result = list(orders_collection.aggregate(popular_course_pipeline))
            most_popular_course_id = popular_course_result[0]["_id"] if popular_course_result else None
            
            most_popular_course = None
            if most_popular_course_id:
                course_doc = courses_collection.find_one({"_id": ObjectId(most_popular_course_id)})
                most_popular_course = course_doc.get("name", "Unknown") if course_doc else "Unknown"
            
            summary = {
                "success": True,
                "generated_at": datetime.now().isoformat(),
                "studio_overview": {
                    "total_clients": total_clients,
                    "active_clients": active_clients,
                    "new_clients_this_month": new_clients_this_month,
                    "client_retention_rate": round((active_clients / total_clients * 100), 2) if total_clients > 0 else 0
                },
                "orders_and_revenue": {
                    "total_orders": total_orders,
                    "active_orders": active_orders,
                    "orders_this_month": orders_this_month,
                    "monthly_revenue": monthly_revenue,
                    "average_order_value": round((monthly_revenue / orders_this_month), 2) if orders_this_month > 0 else 0
                },
                "courses_and_classes": {
                    "available_courses": total_courses,
                    "upcoming_classes": upcoming_classes,
                    "most_popular_course": most_popular_course or "No data available"
                },
                "business_metrics": {
                    "monthly_growth_rate": "Calculation requires historical data",
                    "capacity_utilization": "Calculation requires class capacity data",
                    "customer_satisfaction": "Survey data not available"
                }
            }
            
            return json.dumps(summary, indent=2)
            
        except Exception as e:
            logger.error(f"Summary statistics failed: {str(e)}")
            return f"Summary statistics failed: {str(e)}"
