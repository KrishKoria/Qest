import React from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowLeftIcon,
  UserIcon,
  EnvelopeIcon,
  PhoneIcon,
  CalendarIcon,
  ExclamationTriangleIcon,
  TargetIcon,
} from "@heroicons/react/24/outline";
import { Card, Button, LoadingPage } from "../components/ui";
import { api } from "../services/api";
import { formatDate } from "../utils";

const InfoCard = ({ title, children, icon: Icon }) => (
  <Card className="p-6">
    <div className="flex items-center mb-4">
      {Icon && <Icon className="h-5 w-5 text-gray-400 mr-2" />}
      <h3 className="text-lg font-medium text-gray-900">{title}</h3>
    </div>
    {children}
  </Card>
);

const ClientDetails = () => {
  const { id } = useParams();

  const {
    data: client,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["client", id],
    queryFn: async () => {
      const response = await api.get(`/clients/${id}`);
      return response.data;
    },
    enabled: !!id,
  });

  const { data: orders = [] } = useQuery({
    queryKey: ["client-orders", id],
    queryFn: async () => {
      const response = await api.get(`/clients/${id}/orders`);
      return response.data;
    },
    enabled: !!id,
  });

  const { data: classes = [] } = useQuery({
    queryKey: ["client-classes", id],
    queryFn: async () => {
      const response = await api.get(`/clients/${id}/classes`);
      return response.data;
    },
    enabled: !!id,
  });

  if (isLoading) {
    return <LoadingPage message="Loading client details..." />;
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 text-lg font-semibold mb-2">
          Error loading client
        </div>
        <p className="text-gray-600">
          Client not found or unable to load details
        </p>
        <Link
          to="/clients"
          className="mt-4 inline-block text-blue-600 hover:text-blue-500"
        >
          Back to Clients
        </Link>
      </div>
    );
  }

  if (!client) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Client not found</p>
        <Link
          to="/clients"
          className="mt-4 inline-block text-blue-600 hover:text-blue-500"
        >
          Back to Clients
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link
            to="/clients"
            className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
          >
            <ArrowLeftIcon className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{client.name}</h1>
            <p className="mt-1 text-sm text-gray-600">Client Details</p>
          </div>
        </div>
        <div className="flex space-x-3">
          <Button variant="outline">Edit Client</Button>
          <Button>Create Order</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Personal Information */}
        <div className="lg:col-span-2 space-y-6">
          <InfoCard title="Personal Information" icon={UserIcon}>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <dt className="text-sm font-medium text-gray-500">Full Name</dt>
                <dd className="mt-1 text-sm text-gray-900">{client.name}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Email</dt>
                <dd className="mt-1 text-sm text-gray-900">{client.email}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Phone</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {client.phone || "Not provided"}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">
                  Date of Birth
                </dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {client.date_of_birth
                    ? formatDate(client.date_of_birth)
                    : "Not provided"}
                </dd>
              </div>
              <div className="sm:col-span-2">
                <dt className="text-sm font-medium text-gray-500">
                  Emergency Contact
                </dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {client.emergency_contact || "Not provided"}
                </dd>
              </div>
            </div>
          </InfoCard>

          {client.medical_conditions && (
            <InfoCard title="Medical Conditions" icon={ExclamationTriangleIcon}>
              <p className="text-sm text-gray-900">
                {client.medical_conditions}
              </p>
            </InfoCard>
          )}

          {client.fitness_goals && (
            <InfoCard title="Fitness Goals" icon={TargetIcon}>
              <p className="text-sm text-gray-900">{client.fitness_goals}</p>
            </InfoCard>
          )}

          {/* Recent Orders */}
          <InfoCard title="Recent Orders">
            {orders.length > 0 ? (
              <div className="space-y-3">
                {orders.slice(0, 5).map((order, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between border-b border-gray-200 pb-2"
                  >
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        Order #{order.id}
                      </p>
                      <p className="text-sm text-gray-500">
                        {formatDate(order.created_at)}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">
                        ${order.total || "0.00"}
                      </p>
                      <p className="text-sm text-gray-500">{order.status}</p>
                    </div>
                  </div>
                ))}
                {orders.length > 5 && (
                  <Link
                    to={`/clients/${id}/orders`}
                    className="text-sm text-blue-600 hover:text-blue-500"
                  >
                    View all orders ({orders.length})
                  </Link>
                )}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No orders yet</p>
            )}
          </InfoCard>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <Card className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Quick Stats
            </h3>
            <div className="space-y-4">
              <div>
                <dt className="text-sm font-medium text-gray-500">
                  Total Orders
                </dt>
                <dd className="mt-1 text-2xl font-semibold text-gray-900">
                  {orders.length}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">
                  Classes Attended
                </dt>
                <dd className="mt-1 text-2xl font-semibold text-gray-900">
                  {classes.length}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">
                  Member Since
                </dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {client.created_at
                    ? formatDate(client.created_at)
                    : "Unknown"}
                </dd>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Quick Actions
            </h3>
            <div className="space-y-3">
              <Button className="w-full" variant="outline">
                <EnvelopeIcon className="h-4 w-4 mr-2" />
                Send Email
              </Button>
              <Button className="w-full" variant="outline">
                <PhoneIcon className="h-4 w-4 mr-2" />
                Call Client
              </Button>
              <Button className="w-full" variant="outline">
                <CalendarIcon className="h-4 w-4 mr-2" />
                Schedule Session
              </Button>
            </div>
          </Card>

          {/* Upcoming Classes */}
          <Card className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Upcoming Classes
            </h3>
            {classes.length > 0 ? (
              <div className="space-y-3">
                {classes.slice(0, 3).map((classItem, index) => (
                  <div
                    key={index}
                    className="border-b border-gray-200 pb-2 last:border-b-0"
                  >
                    <p className="text-sm font-medium text-gray-900">
                      {classItem.name}
                    </p>
                    <p className="text-sm text-gray-500">
                      {formatDate(classItem.date)}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No upcoming classes</p>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
};

export default ClientDetails;
