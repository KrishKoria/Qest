import React from "react";
import { useQuery } from "@tanstack/react-query";
import {
  UsersIcon,
  ShoppingBagIcon,
  AcademicCapIcon,
  CalendarIcon,
} from "@heroicons/react/24/outline";
import { Card, LoadingPage } from "../components/ui";
import { api } from "../services/api";
import { TrendingUpIcon } from "lucide-react";

const StatCard = ({
  title,
  value,
  icon: Icon,
  trend,
  trendValue,
  color = "blue",
}) => {
  const colorClasses = {
    blue: "text-blue-600 bg-blue-100",
    green: "text-green-600 bg-green-100",
    yellow: "text-yellow-600 bg-yellow-100",
    purple: "text-purple-600 bg-purple-100",
    red: "text-red-600 bg-red-100",
  };

  return (
    <Card className="p-6">
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <div className={`p-3 rounded-md ${colorClasses[color]}`}>
            <Icon className="h-6 w-6" />
          </div>
        </div>
        <div className="ml-5 w-0 flex-1">
          <dl>
            <dt className="text-sm font-medium text-gray-500 truncate">
              {title}
            </dt>
            <dd className="flex items-baseline">
              <div className="text-2xl font-semibold text-gray-900">
                {value}
              </div>
              {trend && trendValue && (
                <div
                  className={`ml-2 flex items-baseline text-sm font-semibold ${
                    trend === "up" ? "text-green-600" : "text-red-600"
                  }`}
                >
                  <TrendingUpIcon
                    className={`self-center flex-shrink-0 h-4 w-4 ${
                      trend === "down" ? "rotate-180" : ""
                    }`}
                  />
                  <span className="sr-only">
                    {trend === "up" ? "Increased" : "Decreased"} by
                  </span>
                  {trendValue}
                </div>
              )}
            </dd>
          </dl>
        </div>
      </div>
    </Card>
  );
};

const Dashboard = () => {
  // Fetch dashboard statistics using the dashboard agent
  const {
    data: dashboardStats,
    isLoading: statsLoading,
    error: statsError,
  } = useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: api.dashboard.getStats,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  });

  // Fetch recent clients
  const { data: recentClientsData, isLoading: clientsLoading } = useQuery({
    queryKey: ["recent-clients"],
    queryFn: api.dashboard.getRecentClients,
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 1,
  });

  // Fetch recent orders
  const { data: recentOrdersData, isLoading: ordersLoading } = useQuery({
    queryKey: ["recent-orders"],
    queryFn: api.dashboard.getRecentOrders,
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 1,
  });

  if (statsLoading) {
    return <LoadingPage message="Loading dashboard..." />;
  }

  if (statsError) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 text-lg font-semibold mb-2">
          Error loading dashboard
        </div>
        <p className="text-gray-600 mb-4">
          {statsError.message || "Please try refreshing the page"}
        </p>
        <p className="text-sm text-gray-500">
          Make sure the backend is running and your OpenAI API key is configured
        </p>
      </div>
    );
  }

  // Default stats if agent response doesn't provide structured data
  const stats = [
    {
      title: "Total Clients",
      value: "---", // Will be populated by agent response
      icon: UsersIcon,
      color: "blue",
      trend: "up",
      trendValue: "12%",
    },
    {
      title: "Active Orders",
      value: "---", // Will be populated by agent response
      icon: ShoppingBagIcon,
      color: "green",
      trend: "up",
      trendValue: "8%",
    },
    {
      title: "Available Courses",
      value: "---", // Will be populated by agent response
      icon: AcademicCapIcon,
      color: "purple",
    },
    {
      title: "Scheduled Classes",
      value: "---", // Will be populated by agent response
      icon: CalendarIcon,
      color: "yellow",
      trend: "up",
      trendValue: "4%",
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-600">
          Welcome to your fitness studio management dashboard
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, index) => (
          <StatCard key={index} {...stat} />
        ))}
      </div>

      {/* Agent Response Display */}
      {dashboardStats && (
        <Card>
          <Card.Header>
            <Card.Title>Studio Statistics</Card.Title>
          </Card.Header>
          <Card.Content>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-700 whitespace-pre-wrap">
                {dashboardStats.response || "No statistics available"}
              </p>
            </div>
          </Card.Content>
        </Card>
      )}

      {/* Recent Activity */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <Card.Header>
            <Card.Title>Recent Clients</Card.Title>
          </Card.Header>
          <Card.Content>
            {clientsLoading ? (
              <div className="text-center py-4">
                <p className="text-gray-500">Loading clients...</p>
              </div>
            ) : recentClientsData?.response ? (
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-700 whitespace-pre-wrap">
                  {recentClientsData.response}
                </p>
              </div>
            ) : (
              <p className="text-sm text-gray-500">No recent clients data</p>
            )}
          </Card.Content>
        </Card>

        <Card>
          <Card.Header>
            <Card.Title>Recent Orders</Card.Title>
          </Card.Header>
          <Card.Content>
            {ordersLoading ? (
              <div className="text-center py-4">
                <p className="text-gray-500">Loading orders...</p>
              </div>
            ) : recentOrdersData?.response ? (
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-700 whitespace-pre-wrap">
                  {recentOrdersData.response}
                </p>
              </div>
            ) : (
              <p className="text-sm text-gray-500">No recent orders data</p>
            )}
          </Card.Content>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <Card.Header>
          <Card.Title>Quick Actions</Card.Title>
        </Card.Header>
        <Card.Content>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <button className="flex items-center p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
              <UsersIcon className="h-6 w-6 text-blue-600 mr-3" />
              <span className="text-sm font-medium text-blue-900">
                Add Client
              </span>
            </button>
            <button className="flex items-center p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors">
              <ShoppingBagIcon className="h-6 w-6 text-green-600 mr-3" />
              <span className="text-sm font-medium text-green-900">
                Create Order
              </span>
            </button>
            <button className="flex items-center p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors">
              <AcademicCapIcon className="h-6 w-6 text-purple-600 mr-3" />
              <span className="text-sm font-medium text-purple-900">
                Add Course
              </span>
            </button>
            <button className="flex items-center p-4 bg-yellow-50 rounded-lg hover:bg-yellow-100 transition-colors">
              <CalendarIcon className="h-6 w-6 text-yellow-600 mr-3" />
              <span className="text-sm font-medium text-yellow-900">
                Schedule Class
              </span>
            </button>
          </div>
        </Card.Content>
      </Card>
    </div>
  );
};

export default Dashboard;
