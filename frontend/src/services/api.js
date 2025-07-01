import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// Create axios instance with default config
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000, // 30 seconds timeout
});

// Request interceptor for adding auth tokens if needed
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem("authToken");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling common errors
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem("authToken");
      // Don't redirect to login if we don't have auth system
      console.warn("Unauthorized access detected");
    }
    return Promise.reject(error);
  }
);

// API service functions matching the actual backend endpoints
export const api = {
  // Health check
  health: () => apiClient.get("/health"),

  // Agent interactions - These are the actual backend endpoints
  agents: {
    // Support agent queries
    supportQuery: (query, language = "en", context = {}) =>
      apiClient.post("/api/v1/support", { query, language, context }),

    // Dashboard agent queries
    dashboardQuery: (query, language = "en", context = {}) =>
      apiClient.post("/api/v1/dashboard", { query, language, context }),
  },

  // Dashboard data - using agent queries to get data
  dashboard: {
    getStats: async () => {
      // Get dashboard statistics using the dashboard agent
      const response = await apiClient.post("/api/v1/dashboard", {
        query:
          "Give me a summary of studio statistics including total clients, active orders, available courses, and scheduled classes",
        language: "en",
        context: {},
      });
      return response.data;
    },

    getRecentClients: async () => {
      // Get recent clients using support agent
      const response = await apiClient.post("/api/v1/support", {
        query:
          "Show me the 5 most recent clients with their names and email addresses",
        language: "en",
        context: {},
      });
      return response.data;
    },

    getRecentOrders: async () => {
      // Get recent orders using support agent
      const response = await apiClient.post("/api/v1/support", {
        query:
          "Show me the 5 most recent orders with their status and total amount",
        language: "en",
        context: {},
      });
      return response.data;
    },
  },

  // Data queries using agents
  clients: {
    getAll: async (searchQuery = "") => {
      const query = searchQuery
        ? `Find all clients matching: ${searchQuery}`
        : "List all clients with their details";

      const response = await apiClient.post("/api/v1/support", {
        query,
        language: "en",
        context: {},
      });
      return response.data;
    },

    getById: async (id) => {
      const response = await apiClient.post("/api/v1/support", {
        query: `Get details for client with ID: ${id}`,
        language: "en",
        context: {},
      });
      return response.data;
    },

    create: async (clientData) => {
      const response = await apiClient.post("/api/v1/support", {
        query: `Create a new client with details: ${JSON.stringify(
          clientData
        )}`,
        language: "en",
        context: { action: "create_client", data: clientData },
      });
      return response.data;
    },

    search: async (searchTerm) => {
      const response = await apiClient.post("/api/v1/support", {
        query: `Search for clients by name, email, or phone: ${searchTerm}`,
        language: "en",
        context: {},
      });
      return response.data;
    },
  },

  orders: {
    getAll: async (filters = {}) => {
      let query = "List all orders";
      if (filters.status) {
        query += ` with status: ${filters.status}`;
      }
      if (filters.clientId) {
        query += ` for client ID: ${filters.clientId}`;
      }

      const response = await apiClient.post("/api/v1/support", {
        query,
        language: "en",
        context: {},
      });
      return response.data;
    },

    getById: async (id) => {
      const response = await apiClient.post("/api/v1/support", {
        query: `Get order details for order ID: ${id}`,
        language: "en",
        context: {},
      });
      return response.data;
    },

    create: async (orderData) => {
      const response = await apiClient.post("/api/v1/support", {
        query: `Create a new order with details: ${JSON.stringify(orderData)}`,
        language: "en",
        context: { action: "create_order", data: orderData },
      });
      return response.data;
    },
  },

  courses: {
    getAll: async () => {
      const response = await apiClient.post("/api/v1/support", {
        query: "List all available courses with their details",
        language: "en",
        context: {},
      });
      return response.data;
    },

    getById: async (id) => {
      const response = await apiClient.post("/api/v1/support", {
        query: `Get course details for course ID: ${id}`,
        language: "en",
        context: {},
      });
      return response.data;
    },
  },

  classes: {
    getAll: async (filters = {}) => {
      let query = "List all scheduled classes";
      if (filters.upcoming) {
        query = "List upcoming classes this week";
      }
      if (filters.instructor) {
        query += ` by instructor: ${filters.instructor}`;
      }

      const response = await apiClient.post("/api/v1/support", {
        query,
        language: "en",
        context: {},
      });
      return response.data;
    },

    getById: async (id) => {
      const response = await apiClient.post("/api/v1/support", {
        query: `Get class details for class ID: ${id}`,
        language: "en",
        context: {},
      });
      return response.data;
    },
  },

  // Analytics using dashboard agent
  analytics: {
    getRevenue: async (period = "month") => {
      const response = await apiClient.post("/api/v1/dashboard", {
        query: `Show revenue analytics for the current ${period}`,
        language: "en",
        context: {},
      });
      return response.data;
    },

    getClientInsights: async () => {
      const response = await apiClient.post("/api/v1/dashboard", {
        query:
          "Give me client insights including active vs inactive clients and new clients this month",
        language: "en",
        context: {},
      });
      return response.data;
    },

    getAttendance: async () => {
      const response = await apiClient.post("/api/v1/dashboard", {
        query: "Show attendance analytics and class participation rates",
        language: "en",
        context: {},
      });
      return response.data;
    },
  },
};

// Utility functions
export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response;
    console.error(`API Error ${status}:`, data);

    switch (status) {
      case 400:
        return {
          message: data.detail || "Invalid request",
          type: "validation",
        };
      case 401:
        return { message: "Unauthorized access", type: "auth" };
      case 403:
        return { message: "Forbidden access", type: "permission" };
      case 404:
        return { message: "Resource not found", type: "notFound" };
      case 422:
        return {
          message: data.detail || "Validation error",
          type: "validation",
          errors: data.errors,
        };
      case 429:
        return { message: "Too many requests", type: "rateLimit" };
      case 500:
        return { message: "Internal server error", type: "server" };
      default:
        return { message: data.detail || "An error occurred", type: "unknown" };
    }
  } else if (error.request) {
    // Request made but no response received
    console.error("Network Error:", error.request);
    return {
      message: "Network error - please check your connection",
      type: "network",
    };
  } else {
    // Something else happened
    console.error("Error:", error.message);
    return {
      message: error.message || "An unexpected error occurred",
      type: "unknown",
    };
  }
};

export default api;
