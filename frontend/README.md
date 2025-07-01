# Qest Fitness Studio Frontend

A modern, responsive React frontend for the Qest fitness studio management system, powered by CrewAI backend services.

## Features

- **Dashboard**: Overview of studio metrics and quick actions
- **Client Management**: Complete client profiles with fitness goals and medical information
- **Order Management**: Service bookings and order tracking
- **AI Agent Chat**: Interactive chat with specialized fitness AI agents
- **Responsive Design**: Mobile-first approach with modern UI components
- **Real-time Updates**: React Query for efficient data fetching and caching

## Tech Stack

- **Framework**: React 18 with Vite
- **Styling**: Tailwind CSS with custom components
- **State Management**: TanStack Query (React Query) for server state
- **Routing**: React Router v6
- **Icons**: Heroicons
- **HTTP Client**: Axios
- **Notifications**: React Hot Toast
- **Build Tool**: Vite
- **Container**: Docker with Nginx

## Prerequisites

- Node.js 18 or higher
- npm or yarn
- Docker (for containerized deployment)

## Quick Start

### Development

1. **Install dependencies**:

   ```bash
   npm install
   ```

2. **Start development server**:

   ```bash
   npm run dev
   ```

3. **Open browser**: Navigate to `http://localhost:3000`

### Production Build

1. **Build the application**:

   ```bash
   npm run build
   ```

2. **Preview the build**:
   ```bash
   npm run preview
   ```

### Docker Deployment

1. **Build the Docker image**:

   ```bash
   docker build -t qest-frontend .
   ```

2. **Run the container**:
   ```bash
   docker run -p 80:80 qest-frontend
   ```

## Environment Configuration

Create a `.env` file in the root directory:

```env
# Backend API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=10000

# Feature Flags
VITE_ENABLE_DEV_TOOLS=true
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint issues

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Layout/         # Layout components (Header, Sidebar, Layout)
│   └── ui/             # Base UI components (Button, Card, Input, etc.)
├── pages/              # Page components
├── services/           # API services and configuration
├── hooks/              # Custom React hooks
├── utils/              # Utility functions
├── App.jsx             # Main app component
├── main.jsx            # App entry point
└── index.css           # Global styles
```

## Key Features

### Dashboard

- Studio metrics overview
- Recent client and order activity
- Quick action buttons
- Responsive card layout

### Client Management

- Complete client profiles
- Search and filter functionality
- CRUD operations with forms
- Client details with order history

### Order Management

- Service booking system
- Status tracking with visual indicators
- Order filtering and search
- Client association

### AI Agent Chat

- Specialized fitness AI agents:
  - Fitness Coach
  - Nutrition Expert
  - Program Designer
  - Client Advisor
- Real-time chat interface
- Quick action suggestions
- Message history

### UI Components

- Consistent design system
- Accessible components
- Loading states and error handling
- Responsive grid layouts
- Modal dialogs and forms

## API Integration

The frontend integrates with the CrewAI-powered backend through a REST API:

- **Base URL**: Configurable via `VITE_API_BASE_URL`
- **Authentication**: JWT token support (ready for implementation)
- **Error Handling**: Centralized error handling with user-friendly messages
- **Caching**: Optimistic updates with React Query

### Supported Endpoints

- `GET /clients` - List clients
- `POST /clients` - Create client
- `GET /clients/:id` - Get client details
- `PUT /clients/:id` - Update client
- `DELETE /clients/:id` - Delete client
- `GET /orders` - List orders
- `POST /orders` - Create order
- `POST /agent/chat` - Chat with AI agents

## Deployment

### Docker Production Deployment

The application is containerized using a multi-stage Docker build:

1. **Build stage**: Compiles the React application
2. **Production stage**: Serves static files via Nginx

Key features:

- Optimized nginx configuration
- Client-side routing support
- Gzip compression
- Security headers
- Static asset caching

### Environment Variables

For production deployment, configure these environment variables:

- `VITE_API_BASE_URL` - Backend API URL
- `VITE_API_TIMEOUT` - Request timeout (default: 10000ms)

## Development Guidelines

### Code Style

- Use functional components with hooks
- Follow React best practices
- Implement proper error boundaries
- Use TypeScript for type safety (future enhancement)

### State Management

- Use React Query for server state
- Local state with useState for UI state
- Custom hooks for reusable logic

### Component Structure

- Keep components small and focused
- Use composition over inheritance
- Implement proper prop types
- Handle loading and error states

## Future Enhancements

- [ ] TypeScript migration
- [ ] Advanced analytics dashboard
- [ ] Real-time notifications
- [ ] Progressive Web App (PWA) features
- [ ] Advanced form validation
- [ ] Data export functionality
- [ ] Multi-language support
- [ ] Theme customization

## Support

For support and questions:

- Check the backend API documentation
- Review the component documentation
- Check browser console for errors
- Ensure backend is running and accessible

## License

This project is part of the Qest fitness studio management system.
