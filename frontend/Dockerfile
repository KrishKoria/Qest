# Multi-stage build for React application
FROM node:23-alpine AS build

# Set working directory
WORKDIR /app

# Install pnpm globally
RUN npm install -g pnpm

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Clear any existing node_modules and pnpm cache to avoid permission issues
RUN rm -rf node_modules .pnpm-store

# Install dependencies with clean cache
RUN pnpm install --frozen-lockfile --prefer-frozen-lockfile

# Copy source code (excluding node_modules)
COPY . .

# Build the application
RUN pnpm build

# Production stage with nginx
FROM nginx:alpine

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built application from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Install curl for health check
RUN apk --no-cache add curl

# Add health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/health || exit 1

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]