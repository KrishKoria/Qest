#!/bin/bash

# Fitness Studio Agent System - Setup Script
# This script sets up the entire development environment

set -e

echo "🏋️ Fitness Studio Agent System Setup"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check if .env file exists
setup_environment() {
    if [ ! -f ".env" ]; then
        print_status "Creating .env file from template..."
        cp .env.example .env
        print_warning "Please edit .env file with your OpenAI API key and other settings"
        print_warning "Minimal required: OPENAI_API_KEY=your_key_here"
    else
        print_success ".env file already exists"
    fi
}

# Start Docker services
start_services() {
    print_status "Starting Docker services..."
    
    # Pull latest images
    docker-compose pull
    
    # Start core services
    docker-compose up -d mongodb redis
    
    print_status "Waiting for MongoDB to be ready..."
    sleep 10
    
    # Start backend
    docker-compose up -d backend
    
    print_status "Waiting for backend to be ready..."
    sleep 15
    
    print_success "All services are running!"
}

# Generate sample data
generate_sample_data() {
    print_status "Generating sample data..."
    
    # Wait a bit more to ensure backend is fully ready
    sleep 5
    
    if docker-compose exec -T backend python -m app.utils.sample_data; then
        print_success "Sample data generated successfully!"
    else
        print_warning "Sample data generation failed. You can run it manually later:"
        print_warning "docker-compose exec backend python -m app.utils.sample_data"
    fi
}

# Show service status
show_status() {
    echo ""
    print_status "Service Status:"
    docker-compose ps
    
    echo ""
    print_success "Setup completed! 🎉"
    echo ""
    echo "📡 API Endpoints:"
    echo "   • API: http://localhost:8000"
    echo "   • API Documentation: http://localhost:8000/docs"
    echo "   • Health Check: http://localhost:8000/"
    echo ""
    echo "🗄️ Database Management:"
    echo "   • Start MongoDB Express: docker-compose --profile tools up -d mongo-express"
    echo "   • Access: http://localhost:8081 (admin/admin123)"
    echo ""
    echo "🧪 Testing Commands:"
    echo "   • Test Support Agent:"
    echo "     curl -X POST http://localhost:8000/api/v1/support \\"
    echo "       -H 'Content-Type: application/json' \\"
    echo "       -d '{\"query\": \"What classes are available today?\"}'"
    echo ""
    echo "   • Test Dashboard Agent:"
    echo "     curl -X POST http://localhost:8000/api/v1/dashboard \\"
    echo "       -H 'Content-Type: application/json' \\"
    echo "       -d '{\"query\": \"Show me revenue metrics\"}'"
    echo ""
    echo "📊 Logs:"
    echo "   • View backend logs: docker-compose logs -f backend"
    echo "   • View all logs: docker-compose logs -f"
    echo ""
    echo "🛑 Stop Services:"
    echo "   • Stop: docker-compose down"
    echo "   • Reset (remove data): docker-compose down -v"
}

# Main execution
main() {
    echo "Starting setup process..."
    echo ""
    
    check_docker
    setup_environment
    start_services
    generate_sample_data
    show_status
}

# Handle command line arguments
case "${1:-setup}" in
    "setup")
        main
        ;;
    "start")
        print_status "Starting services..."
        docker-compose up -d
        print_success "Services started!"
        ;;
    "stop")
        print_status "Stopping services..."
        docker-compose down
        print_success "Services stopped!"
        ;;
    "reset")
        print_warning "This will remove all data. Are you sure? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            print_status "Resetting environment..."
            docker-compose down -v
            docker system prune -f
            print_success "Environment reset!"
        else
            print_status "Reset cancelled."
        fi
        ;;
    "logs")
        docker-compose logs -f backend
        ;;
    "test")
        print_status "Running quick API tests..."
        echo ""
        
        # Test health endpoint
        echo "Testing health endpoint..."
        if curl -s http://localhost:8000/ | grep -q "Fitness Studio"; then
            print_success "✓ Health check passed"
        else
            print_error "✗ Health check failed"
        fi
        
        # Test support agent
        echo "Testing support agent..."
        response=$(curl -s -X POST http://localhost:8000/api/v1/support \
            -H "Content-Type: application/json" \
            -d '{"query": "What is the status of the system?"}')
        
        if echo "$response" | grep -q "response"; then
            print_success "✓ Support agent test passed"
        else
            print_error "✗ Support agent test failed"
            echo "Response: $response"
        fi
        
        # Test dashboard agent
        echo "Testing dashboard agent..."
        response=$(curl -s -X POST http://localhost:8000/api/v1/dashboard \
            -H "Content-Type: application/json" \
            -d '{"query": "Show system status"}')
        
        if echo "$response" | grep -q "response"; then
            print_success "✓ Dashboard agent test passed"
        else
            print_error "✗ Dashboard agent test failed"
            echo "Response: $response"
        fi
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  setup     Complete setup (default)"
        echo "  start     Start services"
        echo "  stop      Stop services"
        echo "  reset     Reset environment (removes all data)"
        echo "  logs      Show backend logs"
        echo "  test      Run API tests"
        echo "  help      Show this help"
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for available commands"
        exit 1
        ;;
esac
