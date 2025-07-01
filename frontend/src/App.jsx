import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { Toaster } from "react-hot-toast";
import {
  AgentChat,
  Analytics,
  Classes,
  ClientDetails,
  Clients,
  Courses,
  Dashboard,
  NotFound,
  Orders,
  Support,
} from "./pages";
import { Layout } from "./components";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<Dashboard />} />

              {/* Client Management */}
              <Route path="clients" element={<Clients />} />
              <Route path="clients/:id" element={<ClientDetails />} />

              {/* Order Management */}
              <Route path="orders" element={<Orders />} />

              {/* Course & Class Management */}
              <Route path="courses" element={<Courses />} />
              <Route path="classes" element={<Classes />} />

              {/* Analytics */}
              <Route path="analytics" element={<Analytics />} />

              {/* AI Agent */}
              <Route path="agent-chat" element={<AgentChat />} />

              {/* Support */}
              <Route path="support" element={<Support />} />

              {/* 404 */}
              <Route path="*" element={<NotFound />} />
            </Route>
          </Routes>
        </div>
      </Router>

      {/* Toast notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: "#363636",
            color: "#fff",
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: "#10b981",
              secondary: "#fff",
            },
          },
          error: {
            duration: 5000,
            iconTheme: {
              primary: "#ef4444",
              secondary: "#fff",
            },
          },
        }}
      />

      {/* React Query Dev Tools */}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;
