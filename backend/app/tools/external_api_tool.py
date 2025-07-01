from crewai.tools import BaseTool
from typing import Optional, Dict, Any
import json
import requests
import logging
from datetime import datetime
from bson import ObjectId

from ..models.database import get_sync_collection, Collections
from ..models.schemas import CreateClientRequest, CreateOrderRequest, Client, Order

logger = logging.getLogger(__name__)


class ExternalAPITool(BaseTool):
    name: str = "External API Tool"
    description: str = """
    A tool for creating new records and interacting with external services.
    
    Capabilities:
    - Create new client enquiries
    - Create orders for existing or new clients
    - Integrate with external CRM systems
    - Handle payment gateway interactions
    - Send notifications and confirmations
    
    Use this tool when you need to create new records or integrate with external systems.
    """

    def _run(self, action: str, **kwargs) -> str:
        """
        Execute external API operations based on action type.
        
        Args:
            action: Type of action to perform
            **kwargs: Additional parameters for the action
        """
        try:
            if action == "create_client":
                return self._create_client(**kwargs)
            elif action == "create_order":
                return self._create_order(**kwargs)
            elif action == "create_enquiry":
                return self._create_enquiry(**kwargs)
            elif action == "send_notification":
                return self._send_notification(**kwargs)
            elif action == "process_payment":
                return self._process_payment(**kwargs)
            else:
                return f"Unknown action: {action}"
                
        except Exception as e:
            logger.error(f"External API operation failed: {str(e)}")
            return f"External API operation failed: {str(e)}"

    def _create_client(self, name: str, email: str, phone: str, 
                      birthday: Optional[str] = None, address: Optional[str] = None,
                      emergency_contact: Optional[Dict[str, str]] = None, 
                      notes: Optional[str] = None) -> str:
        """Create a new client in the database."""
        try:
            clients_collection = get_sync_collection(Collections.CLIENTS)
            
            # Check if client already exists
            existing_client = clients_collection.find_one({
                "$or": [
                    {"email": email},
                    {"phone": phone}
                ]
            })
            
            if existing_client:
                return json.dumps({
                    "success": False,
                    "message": "Client already exists with this email or phone number",
                    "existing_client_id": str(existing_client["_id"])
                })
            
            # Create new client
            client_data = {
                "name": name,
                "email": email,
                "phone": phone,
                "status": "active",
                "enrolled_services": [],
                "registration_date": datetime.utcnow(),
                "last_activity": datetime.utcnow()
            }
            
            if birthday:
                try:
                    client_data["birthday"] = datetime.fromisoformat(birthday)
                except ValueError:
                    pass  # Invalid date format, skip
            
            if address:
                client_data["address"] = address
            
            if emergency_contact:
                client_data["emergency_contact"] = emergency_contact
                
            if notes:
                client_data["notes"] = notes
            
            # Insert client
            result = clients_collection.insert_one(client_data)
            client_id = str(result.inserted_id)
            
            # Simulate external CRM integration
            self._integrate_with_crm("new_client", {
                "client_id": client_id,
                "name": name,
                "email": email,
                "phone": phone
            })
            
            # Send welcome notification
            self._send_notification(
                action="welcome_email",
                recipient_email=email,
                recipient_name=name,
                message="Welcome to our fitness studio! We're excited to have you join us."
            )
            
            return json.dumps({
                "success": True,
                "message": "Client created successfully",
                "client_id": client_id,
                "client_details": {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "status": "active"
                }
            }, indent=2)
            
        except Exception as e:
            return f"Failed to create client: {str(e)}"

    def _create_order(self, client_email: str, service_type: str, service_name: str,
                     amount: Optional[float] = None, notes: Optional[str] = None) -> str:
        """Create a new order for a client."""
        try:
            clients_collection = get_sync_collection(Collections.CLIENTS)
            orders_collection = get_sync_collection(Collections.ORDERS)
            courses_collection = get_sync_collection(Collections.COURSES)
            classes_collection = get_sync_collection(Collections.CLASSES)
            
            # Find client
            client = clients_collection.find_one({"email": client_email})
            if not client:
                return json.dumps({
                    "success": False,
                    "message": f"Client not found with email: {client_email}"
                })
            
            # Find service
            service = None
            service_collection = courses_collection if service_type == "course" else classes_collection
            service = service_collection.find_one({
                "name": {"$regex": service_name, "$options": "i"}
            })
            
            if not service:
                return json.dumps({
                    "success": False,
                    "message": f"Service not found: {service_name}"
                })
            
            # Determine amount
            if not amount:
                amount = service.get("price", 0)
                if amount == 0:
                    return json.dumps({
                        "success": False,
                        "message": "Service price not available and amount not specified"
                    })
            
            # Create order
            order_data = {
                "client_id": client["_id"],
                "service_type": service_type,
                "service_id": service["_id"],
                "service_name": service["name"],
                "amount": amount,
                "status": "pending",
                "created_date": datetime.utcnow(),
                "due_date": datetime.utcnow().replace(hour=23, minute=59, second=59),  # Due end of day
                "discount_applied": 0.0,
                "tax_amount": amount * 0.1  # 10% tax
            }
            
            if notes:
                order_data["notes"] = notes
            
            # Insert order
            result = orders_collection.insert_one(order_data)
            order_id = str(result.inserted_id)
            
            # Update client's enrolled services
            if service_name not in client.get("enrolled_services", []):
                clients_collection.update_one(
                    {"_id": client["_id"]},
                    {
                        "$push": {"enrolled_services": service_name},
                        "$set": {"last_activity": datetime.utcnow()}
                    }
                )
            
            # Update service enrollment count
            service_collection.update_one(
                {"_id": service["_id"]},
                {"$inc": {"enrollment_count": 1}}
            )
            
            # Simulate external booking system integration
            self._integrate_with_booking_system("new_order", {
                "order_id": order_id,
                "client_email": client_email,
                "service_type": service_type,
                "service_name": service_name,
                "amount": amount
            })
            
            # Send order confirmation
            self._send_notification(
                action="order_confirmation",
                recipient_email=client_email,
                recipient_name=client["name"],
                message=f"Order confirmed for {service_name}. Amount: ${amount:.2f}. Order ID: {order_id}"
            )
            
            return json.dumps({
                "success": True,
                "message": "Order created successfully",
                "order_id": order_id,
                "order_details": {
                    "client_name": client["name"],
                    "client_email": client_email,
                    "service_type": service_type,
                    "service_name": service_name,
                    "amount": amount,
                    "status": "pending",
                    "created_date": order_data["created_date"].isoformat()
                }
            }, indent=2)
            
        except Exception as e:
            return f"Failed to create order: {str(e)}"

    def _create_enquiry(self, name: str, email: str, phone: str, 
                       enquiry_type: str, message: str, 
                       preferred_contact_method: str = "email") -> str:
        """Create a new client enquiry and handle follow-up."""
        try:
            # Create enquiry record (could be stored in a separate collection)
            enquiry_data = {
                "name": name,
                "email": email,
                "phone": phone,
                "enquiry_type": enquiry_type,
                "message": message,
                "preferred_contact_method": preferred_contact_method,
                "status": "new",
                "created_date": datetime.utcnow(),
                "assigned_to": None,
                "follow_up_date": None
            }
            
            # Simulate external CRM integration
            crm_response = self._integrate_with_crm("new_enquiry", enquiry_data)
            
            # Auto-assign based on enquiry type
            assigned_staff = self._assign_enquiry_to_staff(enquiry_type)
            enquiry_data["assigned_to"] = assigned_staff
            
            # Send acknowledgment to client
            self._send_notification(
                action="enquiry_acknowledgment",
                recipient_email=email,
                recipient_name=name,
                message=f"Thank you for your enquiry about {enquiry_type}. We'll get back to you within 24 hours."
            )
            
            # Notify staff
            if assigned_staff:
                self._send_notification(
                    action="staff_notification",
                    recipient_email=f"{assigned_staff}@studio.com",
                    recipient_name=assigned_staff,
                    message=f"New enquiry assigned: {enquiry_type} from {name} ({email})"
                )
            
            return json.dumps({
                "success": True,
                "message": "Enquiry created successfully",
                "enquiry_details": {
                    "name": name,
                    "email": email,
                    "enquiry_type": enquiry_type,
                    "status": "new",
                    "assigned_to": assigned_staff,
                    "created_date": enquiry_data["created_date"].isoformat()
                },
                "crm_integration": crm_response
            }, indent=2)
            
        except Exception as e:
            return f"Failed to create enquiry: {str(e)}"

    def _send_notification(self, action: str, recipient_email: str, 
                          recipient_name: str, message: str) -> str:
        """Send notifications via email or SMS."""
        try:
            # Simulate email sending
            if action in ["welcome_email", "order_confirmation", "enquiry_acknowledgment"]:
                email_sent = self._send_email(recipient_email, recipient_name, message, action)
                
                if email_sent:
                    return json.dumps({
                        "success": True,
                        "message": f"Notification sent successfully to {recipient_email}",
                        "notification_type": action
                    })
                else:
                    return json.dumps({
                        "success": False,
                        "message": "Failed to send notification"
                    })
            
            # For staff notifications, could use internal messaging system
            elif action == "staff_notification":
                return json.dumps({
                    "success": True,
                    "message": f"Staff notification sent: {message}",
                    "notification_type": action
                })
            
            return json.dumps({
                "success": True,
                "message": "Notification processed",
                "notification_type": action
            })
            
        except Exception as e:
            return f"Failed to send notification: {str(e)}"

    def _process_payment(self, order_id: str, amount: float, 
                        payment_method: str, card_details: Optional[Dict] = None) -> str:
        """Process payment through external payment gateway."""
        try:
            # Simulate payment gateway integration
            payment_response = self._integrate_with_payment_gateway({
                "order_id": order_id,
                "amount": amount,
                "payment_method": payment_method,
                "card_details": card_details
            })
            
            if payment_response["success"]:
                # Create payment record
                payments_collection = get_sync_collection(Collections.PAYMENTS)
                orders_collection = get_sync_collection(Collections.ORDERS)
                
                payment_data = {
                    "order_id": ObjectId(order_id),
                    "amount": amount,
                    "payment_date": datetime.utcnow(),
                    "method": payment_method,
                    "status": "completed",
                    "transaction_id": payment_response["transaction_id"],
                    "gateway_response": payment_response
                }
                
                payment_result = payments_collection.insert_one(payment_data)
                
                # Update order status
                orders_collection.update_one(
                    {"_id": ObjectId(order_id)},
                    {
                        "$set": {
                            "status": "paid",
                            "paid_date": datetime.utcnow()
                        }
                    }
                )
                
                return json.dumps({
                    "success": True,
                    "message": "Payment processed successfully",
                    "payment_id": str(payment_result.inserted_id),
                    "transaction_id": payment_response["transaction_id"],
                    "amount": amount
                }, indent=2)
            else:
                return json.dumps({
                    "success": False,
                    "message": "Payment failed",
                    "error": payment_response.get("error", "Unknown error")
                })
                
        except Exception as e:
            return f"Payment processing failed: {str(e)}"

    def _integrate_with_crm(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate integration with external CRM system."""
        # This would typically make HTTP requests to external CRM APIs
        logger.info(f"CRM Integration - Event: {event_type}, Data: {data}")
        
        # Simulate successful CRM integration
        return {
            "success": True,
            "crm_id": f"CRM_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "message": f"Successfully synced {event_type} with CRM"
        }

    def _integrate_with_booking_system(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate integration with external booking system."""
        logger.info(f"Booking System Integration - Event: {event_type}, Data: {data}")
        
        return {
            "success": True,
            "booking_id": f"BOOK_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "message": f"Successfully synced {event_type} with booking system"
        }

    def _integrate_with_payment_gateway(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate payment gateway integration."""
        logger.info(f"Payment Gateway Integration - Data: {payment_data}")
        
        # Simulate payment processing with 95% success rate
        import random
        success = random.random() > 0.05
        
        if success:
            return {
                "success": True,
                "transaction_id": f"TXN_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}",
                "gateway_response_code": "00",
                "message": "Payment processed successfully"
            }
        else:
            return {
                "success": False,
                "error": "Payment declined by bank",
                "gateway_response_code": "05"
            }

    def _send_email(self, email: str, name: str, message: str, template_type: str) -> bool:
        """Simulate email sending."""
        logger.info(f"Sending email to {email} - Template: {template_type}")
        
        # In a real implementation, this would integrate with email services
        # like SendGrid, AWS SES, or similar
        
        email_templates = {
            "welcome_email": f"Welcome {name}! {message}",
            "order_confirmation": f"Hi {name}, {message}",
            "enquiry_acknowledgment": f"Dear {name}, {message}"
        }
        
        email_content = email_templates.get(template_type, message)
        
        # Simulate successful email sending (95% success rate)
        import random
        return random.random() > 0.05

    def _assign_enquiry_to_staff(self, enquiry_type: str) -> str:
        """Auto-assign enquiries to appropriate staff members."""
        staff_assignments = {
            "yoga": "Sarah Johnson",
            "pilates": "Mike Chen",
            "fitness": "Jessica Williams",
            "membership": "Alex Rodriguez",
            "general": "Customer Service Team"
        }
        
        # Match enquiry type to staff
        for key, staff in staff_assignments.items():
            if key.lower() in enquiry_type.lower():
                return staff
        
        return staff_assignments["general"]
