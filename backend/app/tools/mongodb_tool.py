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
            if query_type == "find_clients":
                return self._find_clients(**kwargs)
            elif query_type == "get_client_by_id":
                return self._get_client_by_id(**kwargs)
            elif query_type == "search_clients":
                return self._search_clients(**kwargs)
            elif query_type == "get_orders":
                return self._get_orders(**kwargs)
            elif query_type == "get_order_by_id":
                return self._get_order_by_id(**kwargs)
            elif query_type == "get_payments":
                return self._get_payments(**kwargs)
            elif query_type == "get_courses":
                return self._get_courses(**kwargs)
            elif query_type == "get_classes":
                return self._get_classes(**kwargs)
            elif query_type == "get_attendance":
                return self._get_attendance(**kwargs)
            elif query_type == "revenue_analytics":
                return self._revenue_analytics(**kwargs)
            elif query_type == "client_analytics":
                return self._client_analytics(**kwargs)
            elif query_type == "service_analytics":
                return self._service_analytics(**kwargs)
            elif query_type == "attendance_analytics":
                return self._attendance_analytics(**kwargs)
            else:
                return f"Unknown query type: {query_type}"
                
        except Exception as e:
            logger.error(f"MongoDB operation failed: {str(e)}")
            return f"Database operation failed: {str(e)}"

    def _find_clients(self, status: Optional[str] = None, limit: int = 50) -> str:
        """Find clients with optional status filter."""
        try:
            collection = get_sync_collection(Collections.CLIENTS)
            filter_dict = {}
            
            if status:
                filter_dict["status"] = status
                
            clients = list(collection.find(filter_dict).limit(limit))
            
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
