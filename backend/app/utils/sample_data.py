"""
Sample data generator for the fitness studio database.
This script creates realistic sample data for testing and demonstration purposes.
"""

import asyncio
from datetime import datetime, timedelta
import random
from typing import List, Dict
import logging

from ..models.database import DatabaseManager, get_collection, Collections
from ..models.schemas import ClientStatus, OrderStatus, PaymentStatus, AttendanceStatus

logger = logging.getLogger(__name__)

class SampleDataGenerator:
    """Generates realistic sample data for the fitness studio."""
    
    def __init__(self):
        self.first_names = [
            "Emma", "Liam", "Olivia", "Noah", "Ava", "Oliver", "Sophia", "Elijah",
            "Charlotte", "William", "Amelia", "James", "Isabella", "Benjamin", "Mia",
            "Lucas", "Harper", "Henry", "Evelyn", "Alexander", "Abigail", "Mason",
            "Emily", "Michael", "Elizabeth", "Ethan", "Sofia", "Daniel", "Avery",
            "Jacob", "Ella", "Logan", "Scarlett", "Jackson", "Grace", "Levi",
            "Chloe", "Sebastian", "Victoria", "Mateo", "Riley", "Jack", "Aria",
            "Owen", "Lily", "Theodore", "Aubrey", "Aiden", "Zoey", "Samuel"
        ]
        
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
            "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
            "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
            "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
            "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
            "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
            "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
            "Carter", "Roberts"
        ]
        
        self.course_data = [
            {
                "name": "Yoga Beginner",
                "instructor": "Sarah Johnson",
                "description": "Perfect for newcomers to yoga. Learn basic poses, breathing techniques, and relaxation methods.",
                "duration_weeks": 8,
                "capacity": 15,
                "price": 120.00,
                "category": "Yoga",
                "difficulty_level": "beginner"
            },
            {
                "name": "Advanced Pilates",
                "instructor": "Michael Chen",
                "description": "High-intensity Pilates for experienced practitioners. Focus on core strength and flexibility.",
                "duration_weeks": 12,
                "capacity": 10,
                "price": 180.00,
                "category": "Pilates",
                "difficulty_level": "advanced"
            },
            {
                "name": "HIIT Bootcamp",
                "instructor": "Lisa Rodriguez",
                "description": "High-Intensity Interval Training for maximum calorie burn and muscle building.",
                "duration_weeks": 6,
                "capacity": 20,
                "price": 150.00,
                "category": "Cardio",
                "difficulty_level": "intermediate"
            },
            {
                "name": "Meditation & Mindfulness",
                "instructor": "David Kim",
                "description": "Learn mindfulness techniques and meditation practices for stress relief and mental clarity.",
                "duration_weeks": 4,
                "capacity": 12,
                "price": 80.00,
                "category": "Wellness",
                "difficulty_level": "beginner"
            },
            {
                "name": "Strength Training",
                "instructor": "Amanda Wilson",
                "description": "Build muscle and increase strength with progressive weight training programs.",
                "duration_weeks": 10,
                "capacity": 8,
                "price": 200.00,
                "category": "Strength",
                "difficulty_level": "intermediate"
            },
            {
                "name": "Dance Fitness",
                "instructor": "Carlos Martinez",
                "description": "Fun and energetic dance-based workout combining various dance styles.",
                "duration_weeks": 8,
                "capacity": 25,
                "price": 140.00,
                "category": "Dance",
                "difficulty_level": "beginner"
            }
        ]
        
        self.instructors = [
            "Sarah Johnson", "Michael Chen", "Lisa Rodriguez", 
            "David Kim", "Amanda Wilson", "Carlos Martinez",
            "Jennifer Lee", "Robert Taylor", "Maya Patel"
        ]

    async def generate_all_sample_data(self):
        """Generate all sample data."""
        logger.info("Starting sample data generation...")
        
        # Connect to database
        await DatabaseManager.connect_to_mongo()
        
        # Clear existing data (optional)
        await self._clear_existing_data()
        
        # Generate data in order (dependencies)
        clients = await self._generate_clients(50)
        courses = await self._generate_courses()
        classes = await self._generate_classes(courses)
        orders = await self._generate_orders(clients, courses, classes)
        payments = await self._generate_payments(orders)
        attendance = await self._generate_attendance(clients, classes)
        
        logger.info("Sample data generation completed!")
        
        # Print summary
        await self._print_summary()

    async def _clear_existing_data(self):
        """Clear existing sample data."""
        collections = [
            Collections.CLIENTS,
            Collections.ORDERS,
            Collections.PAYMENTS,
            Collections.COURSES,
            Collections.CLASSES,
            Collections.ATTENDANCE
        ]
        
        for collection_name in collections:
            collection = get_collection(collection_name)
            await collection.delete_many({})
        
        logger.info("Existing data cleared")

    async def _generate_clients(self, count: int) -> List[Dict]:
        """Generate sample clients."""
        clients = []
        collection = get_collection(Collections.CLIENTS)
        
        for i in range(count):
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            
            # Generate registration date (last 2 years)
            registration_date = datetime.utcnow() - timedelta(
                days=random.randint(1, 730)
            )
            
            # Generate birthday (20-60 years old)
            age_years = random.randint(20, 60)
            birthday = datetime.utcnow() - timedelta(days=age_years * 365 + random.randint(0, 365))
            
            client = {
                "name": f"{first_name} {last_name}",
                "email": f"{first_name.lower()}.{last_name.lower()}@email.com",
                "phone": f"+1{random.randint(1000000000, 9999999999)}",
                "status": random.choice(list(ClientStatus)),
                "enrolled_services": [],
                "registration_date": registration_date,
                "birthday": birthday,
                "last_activity": registration_date + timedelta(
                    days=random.randint(0, (datetime.utcnow() - registration_date).days)
                ),
                "address": f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Park', 'Elm', 'First'])} St, City, State",
                "emergency_contact": {
                    "name": f"{random.choice(self.first_names)} {random.choice(self.last_names)}",
                    "phone": f"+1{random.randint(1000000000, 9999999999)}",
                    "relationship": random.choice(["spouse", "parent", "sibling", "friend"])
                }
            }
            
            clients.append(client)
        
        # Insert clients
        await collection.insert_many(clients)
        logger.info(f"Generated {count} clients")
        
        return clients

    async def _generate_courses(self) -> List[Dict]:
        """Generate sample courses."""
        courses = []
        collection = get_collection(Collections.COURSES)
        
        for course_data in self.course_data:
            course = {
                **course_data,
                "enrollment_count": random.randint(5, course_data["capacity"]),
                "completion_rate": round(random.uniform(70, 95), 1),
                "prerequisites": [],
                "is_active": True,
                "created_date": datetime.utcnow() - timedelta(days=random.randint(30, 365))
            }
            courses.append(course)
        
        # Insert courses
        await collection.insert_many(courses)
        logger.info(f"Generated {len(courses)} courses")
        
        return courses

    async def _generate_classes(self, courses: List[Dict]) -> List[Dict]:
        """Generate sample classes."""
        classes = []
        collection = get_collection(Collections.CLASSES)
        
        # Get course IDs after insertion
        courses_collection = get_collection(Collections.COURSES)
        db_courses = await courses_collection.find({}).to_list(length=None)
        
        for course in db_courses:
            # Generate 10-20 classes per course
            num_classes = random.randint(10, 20)
            
            for i in range(num_classes):
                # Generate class schedule (next 60 days)
                schedule = datetime.utcnow() + timedelta(
                    days=random.randint(1, 60),
                    hours=random.randint(6, 20),
                    minutes=random.choice([0, 15, 30, 45])
                )
                
                class_item = {
                    "course_id": course["_id"],
                    "course_name": course["name"],
                    "instructor": course["instructor"],
                    "schedule": schedule,
                    "duration_minutes": random.choice([45, 60, 75, 90]),
                    "capacity": course["capacity"],
                    "enrolled_count": random.randint(0, course["capacity"]),
                    "room": f"Studio {random.choice(['A', 'B', 'C'])}",
                    "equipment_needed": random.sample([
                        "yoga mats", "dumbbells", "resistance bands", 
                        "stability balls", "foam rollers"
                    ], random.randint(1, 3)),
                    "is_cancelled": random.choice([False] * 9 + [True]),  # 10% cancellation rate
                    "notes": "Regular class session"
                }
                
                if class_item["is_cancelled"]:
                    class_item["cancellation_reason"] = random.choice([
                        "Instructor illness", "Low enrollment", "Facility maintenance"
                    ])
                
                classes.append(class_item)
        
        # Insert classes
        await collection.insert_many(classes)
        logger.info(f"Generated {len(classes)} classes")
        
        return classes

    async def _generate_orders(self, clients: List[Dict], courses: List[Dict], classes: List[Dict]) -> List[Dict]:
        """Generate sample orders."""
        orders = []
        collection = get_collection(Collections.ORDERS)
        
        # Get actual client and course IDs from database
        clients_collection = get_collection(Collections.CLIENTS)
        courses_collection = get_collection(Collections.COURSES)
        
        db_clients = await clients_collection.find({}).to_list(length=None)
        db_courses = await courses_collection.find({}).to_list(length=None)
        
        # Generate 100-150 orders
        num_orders = random.randint(100, 150)
        
        for i in range(num_orders):
            client = random.choice(db_clients)
            course = random.choice(db_courses)
            
            # Generate order date (last 6 months)
            created_date = datetime.utcnow() - timedelta(
                days=random.randint(1, 180)
            )
            
            order = {
                "client_id": client["_id"],
                "service_type": "course",
                "service_id": course["_id"],
                "service_name": course["name"],
                "amount": course["price"],
                "status": random.choice(list(OrderStatus)),
                "created_date": created_date,
                "discount_applied": round(random.uniform(0, 20), 2) if random.random() < 0.3 else 0,
                "tax_amount": round(course["price"] * 0.08, 2),  # 8% tax
                "notes": random.choice([
                    "", "Student discount applied", "Early bird special", 
                    "Referral bonus", "Loyalty member discount"
                ])
            }
            
            # Set due date and paid date based on status
            if order["status"] in ["paid", "refunded"]:
                order["due_date"] = created_date + timedelta(days=7)
                order["paid_date"] = created_date + timedelta(days=random.randint(1, 7))
            elif order["status"] == "pending":
                order["due_date"] = datetime.utcnow() + timedelta(days=random.randint(1, 30))
            
            orders.append(order)
        
        # Insert orders
        await collection.insert_many(orders)
        logger.info(f"Generated {len(orders)} orders")
        
        return orders

    async def _generate_payments(self, orders: List[Dict]) -> List[Dict]:
        """Generate sample payments."""
        payments = []
        collection = get_collection(Collections.PAYMENTS)
        
        # Get actual orders from database
        orders_collection = get_collection(Collections.ORDERS)
        db_orders = await orders_collection.find({}).to_list(length=None)
        
        for order in db_orders:
            if order["status"] in ["paid", "refunded"]:
                payment = {
                    "order_id": order["_id"],
                    "amount": order["amount"] - order.get("discount_applied", 0) + order.get("tax_amount", 0),
                    "payment_date": order.get("paid_date", order["created_date"]),
                    "method": random.choice(["card", "cash", "online", "bank_transfer"]),
                    "status": PaymentStatus.COMPLETED if order["status"] == "paid" else PaymentStatus.REFUNDED,
                    "transaction_id": f"TXN{random.randint(1000000, 9999999)}",
                    "gateway_response": {
                        "status": "success",
                        "reference": f"REF{random.randint(100000, 999999)}"
                    }
                }
                payments.append(payment)
        
        # Insert payments
        if payments:
            await collection.insert_many(payments)
        logger.info(f"Generated {len(payments)} payments")
        
        return payments

    async def _generate_attendance(self, clients: List[Dict], classes: List[Dict]) -> List[Dict]:
        """Generate sample attendance records."""
        attendance_records = []
        collection = get_collection(Collections.ATTENDANCE)
        
        # Get actual clients and classes from database
        clients_collection = get_collection(Collections.CLIENTS)
        classes_collection = get_collection(Collections.CLASSES)
        
        db_clients = await clients_collection.find({}).to_list(length=None)
        db_classes = await classes_collection.find({}).to_list(length=None)
        
        # Generate attendance for past classes
        past_classes = [c for c in db_classes if c["schedule"] < datetime.utcnow()]
        
        for class_item in past_classes:
            # Randomly select clients for this class (60-90% attendance rate)
            num_attendees = int(class_item["enrolled_count"] * random.uniform(0.6, 0.9))
            attending_clients = random.sample(db_clients, min(num_attendees, len(db_clients)))
            
            for client in attending_clients:
                attendance = {
                    "class_id": class_item["_id"],
                    "client_id": client["_id"],
                    "date": class_item["schedule"],
                    "status": random.choice([
                        AttendanceStatus.PRESENT,
                        AttendanceStatus.PRESENT,
                        AttendanceStatus.PRESENT,
                        AttendanceStatus.LATE,
                        AttendanceStatus.ABSENT
                    ]),  # 75% present, 20% late, 5% absent
                    "checked_in_time": class_item["schedule"] + timedelta(
                        minutes=random.randint(-5, 15)
                    ) if random.random() > 0.1 else None,
                    "checked_out_time": class_item["schedule"] + timedelta(
                        minutes=class_item["duration_minutes"] + random.randint(-10, 20)
                    ) if random.random() > 0.2 else None
                }
                
                attendance_records.append(attendance)
        
        # Insert attendance records
        if attendance_records:
            await collection.insert_many(attendance_records)
        logger.info(f"Generated {len(attendance_records)} attendance records")
        
        return attendance_records

    async def _print_summary(self):
        """Print a summary of generated data."""
        collections_data = {}
        
        for collection_name in [
            Collections.CLIENTS, Collections.ORDERS, Collections.PAYMENTS,
            Collections.COURSES, Collections.CLASSES, Collections.ATTENDANCE
        ]:
            collection = get_collection(collection_name)
            count = await collection.count_documents({})
            collections_data[collection_name] = count
        
        print("\n" + "="*50)
        print("SAMPLE DATA GENERATION SUMMARY")
        print("="*50)
        for collection_name, count in collections_data.items():
            print(f"{collection_name.capitalize()}: {count} records")
        print("="*50)


async def generate_sample_data():
    """Main function to generate sample data."""
    generator = SampleDataGenerator()
    await generator.generate_all_sample_data()


if __name__ == "__main__":
    asyncio.run(generate_sample_data())
