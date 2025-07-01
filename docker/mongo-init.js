// MongoDB initialization script
// This script runs when the MongoDB container starts for the first time

// Switch to the fitness_studio database
db = db.getSiblingDB('fitness_studio');

// Create collections with validation
db.createCollection('clients', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['name', 'email', 'phone', 'status'],
      properties: {
        name: {
          bsonType: 'string',
          description: 'Client name is required'
        },
        email: {
          bsonType: 'string',
          pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
          description: 'Valid email is required'
        },
        phone: {
          bsonType: 'string',
          description: 'Phone number is required'
        },
        status: {
          bsonType: 'string',
          enum: ['active', 'inactive', 'suspended'],
          description: 'Status must be active, inactive, or suspended'
        }
      }
    }
  }
});

db.createCollection('orders');
db.createCollection('payments');
db.createCollection('courses');
db.createCollection('classes');
db.createCollection('attendance');

// Create indexes
print('Creating indexes...');

// Clients indexes
db.clients.createIndex({ 'email': 1 }, { unique: true });
db.clients.createIndex({ 'phone': 1 });
db.clients.createIndex({ 'name': 'text', 'email': 'text' });
db.clients.createIndex({ 'status': 1 });

// Orders indexes
db.orders.createIndex({ 'client_id': 1 });
db.orders.createIndex({ 'status': 1 });
db.orders.createIndex({ 'created_date': -1 });
db.orders.createIndex({ 'service_type': 1, 'service_id': 1 });

// Payments indexes
db.payments.createIndex({ 'order_id': 1 });
db.payments.createIndex({ 'status': 1 });
db.payments.createIndex({ 'payment_date': -1 });

// Courses indexes
db.courses.createIndex({ 'name': 'text', 'description': 'text' });
db.courses.createIndex({ 'instructor': 1 });
db.courses.createIndex({ 'category': 1 });
db.courses.createIndex({ 'is_active': 1 });

// Classes indexes
db.classes.createIndex({ 'course_id': 1 });
db.classes.createIndex({ 'instructor': 1 });
db.classes.createIndex({ 'schedule': 1 });
db.classes.createIndex({ 'is_cancelled': 1 });

// Attendance indexes
db.attendance.createIndex({ 'class_id': 1, 'client_id': 1 }, { unique: true });
db.attendance.createIndex({ 'client_id': 1 });
db.attendance.createIndex({ 'date': -1 });
db.attendance.createIndex({ 'status': 1 });

print('Database initialization completed successfully!');
print('Collections created: clients, orders, payments, courses, classes, attendance');
print('Indexes created for optimal performance');
