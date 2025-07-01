# 🏋️ Fitness Studio Agent System

A comprehensive AI-powered customer support and business analytics system for fitness studios, built with CrewAI, FastAPI, and MongoDB.

## 🌟 Features

### 🤖 AI Agents
- **Support Agent**: Handles customer queries about courses, orders, payments, and bookings
- **Dashboard Agent**: Provides business analytics, metrics, and insights

### 🛠️ Core Capabilities
- **Natural Language Processing**: Understands queries in multiple languages
- **MongoDB Integration**: Efficient data storage and retrieval
- **External API Integration**: Seamless creation of clients and orders
- **Real-time Analytics**: Business metrics and performance insights
- **Memory & Context**: Agents remember conversation context

### 📊 Data Management
- Client management and enrollment tracking
- Order and payment processing
- Course and class scheduling
- Attendance monitoring
- Revenue and performance analytics

## 🏗️ Architecture

```
backend/
├── app/
│   ├── agents/           # CrewAI agent management
│   ├── api/             # FastAPI routes and endpoints
│   ├── config/          # Agent configurations (YAML)
│   ├── models/          # Database models and schemas
│   ├── tools/           # Custom CrewAI tools
│   ├── utils/           # Utilities and sample data
│   └── main.py          # FastAPI application entry point
├── requirements.txt     # Python dependencies
└── .env.example        # Environment configuration template
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB 4.4+
- OpenAI API key (for CrewAI)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/fitness-studio-agents.git
   cd fitness-studio-agents/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start MongoDB**
   ```bash
   mongod
   ```

6. **Generate sample data**
   ```bash
   python -m app.utils.sample_data
   ```

7. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## 🔧 Configuration

### Environment Variables

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=fitness_studio

# OpenAI Configuration (for CrewAI)
OPENAI_API_KEY=your_openai_api_key_here

# External API Configuration
EXTERNAL_API_BASE_URL=https://api.example.com
EXTERNAL_API_KEY=your_external_api_key_here

# Application Configuration
DEBUG=true
LOG_LEVEL=INFO
```

### Agent Configuration

Agents are configured in `app/config/agents.yaml`:

```yaml
support_agent:
  role: Customer Support Specialist for Fitness Studio
  goal: Provide exceptional customer service...
  backstory: You are an experienced customer support specialist...
  verbose: true
  memory: true

dashboard_agent:
  role: Business Intelligence Analyst for Fitness Studio
  goal: Provide comprehensive business analytics...
  backstory: You are a skilled business analyst...
  verbose: true
  memory: true
```

## 📡 API Endpoints

### Agent Interactions

#### Support Agent
```http
POST /api/v1/support
Content-Type: application/json

{
  "query": "What classes are available this week?",
  "language": "en",
  "context": {}
}
```

#### Dashboard Agent
```http
POST /api/v1/dashboard
Content-Type: application/json

{
  "query": "How much revenue did we generate this month?",
  "language": "en",
  "context": {}
}
```

### Data Management

#### Clients
- `GET /api/v1/clients` - List clients
- `GET /api/v1/clients/{id}` - Get client by ID
- `POST /api/v1/clients` - Create new client

#### Orders
- `GET /api/v1/orders` - List orders
- `POST /api/v1/orders` - Create new order

#### Courses & Classes
- `GET /api/v1/courses` - List courses
- `GET /api/v1/classes` - List classes

#### Analytics
- `GET /api/v1/analytics/revenue` - Revenue metrics
- `GET /api/v1/analytics/clients` - Client analytics

## 🤖 Agent Usage Examples

### Support Agent Queries

```python
# Client search
"Find all information about client John Doe"

# Order status
"Has order #12345 been paid?"

# Class scheduling
"What yoga classes are available next week?"

# Booking creation
"Create an order for Pilates Beginner for client sarah@email.com"
```

### Dashboard Agent Queries

```python
# Revenue analytics
"What's our total revenue for this month?"

# Client insights
"How many new clients did we get this month?"

# Service performance
"Which course has the highest enrollment?"

# Attendance analytics
"What's the attendance rate for HIIT classes?"
```

## 🗄️ Database Schema

### Collections

#### Clients
```javascript
{
  "_id": ObjectId,
  "name": "John Doe",
  "email": "john@email.com",
  "phone": "+1234567890",
  "status": "active",
  "enrolled_services": [],
  "registration_date": ISODate,
  "birthday": ISODate,
  "last_activity": ISODate
}
```

#### Orders
```javascript
{
  "_id": ObjectId,
  "client_id": ObjectId,
  "service_type": "course",
  "service_id": ObjectId,
  "service_name": "Yoga Beginner",
  "amount": 120.00,
  "status": "paid",
  "created_date": ISODate,
  "paid_date": ISODate
}
```

#### Courses
```javascript
{
  "_id": ObjectId,
  "name": "Yoga Beginner",
  "instructor": "Sarah Johnson",
  "description": "Perfect for newcomers...",
  "duration_weeks": 8,
  "capacity": 15,
  "price": 120.00,
  "category": "Yoga"
}
```

#### Classes
```javascript
{
  "_id": ObjectId,
  "course_id": ObjectId,
  "instructor": "Sarah Johnson",
  "schedule": ISODate,
  "duration_minutes": 60,
  "capacity": 15,
  "room": "Studio A"
}
```

## 🧪 Testing

### Sample Data Generation

Generate realistic test data:

```bash
python -m app.utils.sample_data
```

This creates:
- 50 sample clients
- 6 courses with multiple classes
- 100+ orders with payments
- Attendance records

### Manual Testing

```bash
# Test support agent
curl -X POST "http://localhost:8000/api/v1/support" \
  -H "Content-Type: application/json" \
  -d '{"query": "What classes are available today?"}'

# Test dashboard agent
curl -X POST "http://localhost:8000/api/v1/dashboard" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me revenue metrics for this month"}'
```

## 🌟 Bonus Features

### Multilingual Support
The system automatically detects query language and responds appropriately:

```python
# English
"What classes are available today?"

# Spanish
"¿Qué clases están disponibles hoy?"

# French
"Quels cours sont disponibles aujourd'hui?"
```

### Memory & Context
Agents remember conversation context:

```python
# First query
"Tell me about client John Doe"

# Follow-up query (remembers John Doe context)
"What orders does he have?"
```

### RAG (Retrieval-Augmented Generation)
Smart querying with context from the knowledge base for more accurate responses.

## 🔒 Security

- Input validation with Pydantic models
- MongoDB query sanitization
- Environment-based configuration
- Error handling and logging

## 📈 Performance

- MongoDB indexing for optimal query performance
- Connection pooling for database efficiency
- Async operations where possible
- Caching with Redis (optional)

## 🚀 Deployment

### Docker Deployment

### Quick Start with Docker Compose

The easiest way to run the entire system is using Docker Compose:

1. **Clone and setup**
   ```bash
   git clone https://github.com/yourusername/fitness-studio-agents.git
   cd fitness-studio-agents
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Generate sample data**
   ```bash
   docker-compose exec backend python -m app.utils.sample_data
   ```

4. **Access the services**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - MongoDB Express: http://localhost:8081 (username: admin, password: admin123)

### Docker Compose Services

#### Core Services (always running)
- **backend**: FastAPI application with CrewAI agents
- **mongodb**: MongoDB database with pre-configured collections
- **redis**: Redis for caching and agent memory

#### Optional Services
- **frontend**: React frontend (use `--profile frontend`)
- **mongo-express**: Database management UI (use `--profile tools`)

### Docker Commands

```bash
# Start core services only
docker-compose up -d

# Start with frontend
docker-compose --profile frontend up -d

# Start with all tools
docker-compose --profile frontend --profile tools up -d

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down

# Remove all data (reset)
docker-compose down -v
```

### Development with Docker

For development with live code reloading:

```bash
# Start dependencies only
docker-compose up -d mongodb redis

# Run backend locally
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Environment Configuration

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_change_in_production
EXTERNAL_API_BASE_URL=https://api.example.com
EXTERNAL_API_KEY=your_external_api_key_here
```

### Docker Health Checks

All services include health checks:

```bash
# Check service health
docker-compose ps

# View health check logs
docker inspect fitness_studio_backend --format='{{.State.Health.Status}}'
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the example queries

## 🎯 Roadmap

- [ ] Enhanced multilingual support
- [ ] Advanced analytics dashboards
- [ ] Mobile app integration
- [ ] Automated email notifications
- [ ] Advanced scheduling features
- [ ] Payment gateway integration
- [ ] Instructor portal

---

**Built with ❤️ using CrewAI, FastAPI, and MongoDB**
