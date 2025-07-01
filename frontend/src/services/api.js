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
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// API service functions
export const api = {
  // Health check
  health: () => apiClient.get("/health"),

  // Agent interactions
  agents: {
    query: (query, agentType = "support") =>
      apiClient.post("/agents/query", { query, agent_type: agentType }),

    getAvailableAgents: () => apiClient.get("/agents/available"),

    getAgentCapabilities: (agentType) =>
      apiClient.get(`/agents/${agentType}/capabilities`),
  },

  // Members management
  members: {
    getAll: (params = {}) => apiClient.get("/members", { params }),

    getById: (id) => apiClient.get(`/members/${id}`),

    create: (memberData) => apiClient.post("/members", memberData),

    update: (id, memberData) => apiClient.put(`/members/${id}`, memberData),

    delete: (id) => apiClient.delete(`/members/${id}`),

    search: (query) =>
      apiClient.get("/members/search", { params: { q: query } }),
  },

  // Classes management
  classes: {
    getAll: (params = {}) => apiClient.get("/classes", { params }),

    getById: (id) => apiClient.get(`/classes/${id}`),

    create: (classData) => apiClient.post("/classes", classData),

    update: (id, classData) => apiClient.put(`/classes/${id}`, classData),

    delete: (id) => apiClient.delete(`/classes/${id}`),

    getUpcoming: () => apiClient.get("/classes/upcoming"),

    getByInstructor: (instructorId) =>
      apiClient.get(`/classes/instructor/${instructorId}`),
  },

  // Instructors management
  instructors: {
    getAll: (params = {}) => apiClient.get("/instructors", { params }),

    getById: (id) => apiClient.get(`/instructors/${id}`),

    create: (instructorData) => apiClient.post("/instructors", instructorData),

    update: (id, instructorData) =>
      apiClient.put(`/instructors/${id}`, instructorData),

    delete: (id) => apiClient.delete(`/instructors/${id}`),

    getSchedule: (id, params = {}) =>
      apiClient.get(`/instructors/${id}/schedule`, { params }),
  },

  // Memberships management
  memberships: {
    getAll: (params = {}) => apiClient.get("/memberships", { params }),

    getById: (id) => apiClient.get(`/memberships/${id}`),

    create: (membershipData) => apiClient.post("/memberships", membershipData),

    update: (id, membershipData) =>
      apiClient.put(`/memberships/${id}`, membershipData),

    delete: (id) => apiClient.delete(`/memberships/${id}`),

    getActive: () => apiClient.get("/memberships/active"),

    getExpiring: (days = 30) =>
      apiClient.get("/memberships/expiring", { params: { days } }),
  },

  // Analytics and reporting
  analytics: {
    getDashboard: () => apiClient.get("/analytics/dashboard"),

    getMembershipStats: (params = {}) =>
      apiClient.get("/analytics/memberships", { params }),

    getRevenueStats: (params = {}) =>
      apiClient.get("/analytics/revenue", { params }),

    getClassAttendance: (params = {}) =>
      apiClient.get("/analytics/attendance", { params }),

    getInstructorPerformance: (params = {}) =>
      apiClient.get("/analytics/instructors", { params }),

    getCustomReport: (reportType, params = {}) =>
      apiClient.get(`/analytics/reports/${reportType}`, { params }),
  },

  // External integrations (if needed)
  external: {
    getWeather: () => apiClient.get("/external/weather"),

    getHealthData: (params = {}) =>
      apiClient.get("/external/health", { params }),
  },

  // File uploads
  uploads: {
    uploadFile: (file, type = "general") => {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("type", type);

      return apiClient.post("/uploads", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
    },

    uploadAvatar: (file, entityType, entityId) => {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("entity_type", entityType);
      formData.append("entity_id", entityId);

      return apiClient.post("/uploads/avatar", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
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
