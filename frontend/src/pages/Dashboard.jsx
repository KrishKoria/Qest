import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  UsersIcon, 
  ShoppingBagIcon, 
  AcademicCapIcon,
  ChartBarIcon,
  CalendarIcon,
  TrendingUpIcon
} from '@heroicons/react/24/outline';
import { Card, LoadingPage } from '../components/ui';
import { api } from '../services/api';

const StatCard = ({ title, value, icon: Icon, trend, trendValue, color = 'blue' }) => {
  const colorClasses = {
    blue: 'text-blue-600 bg-blue-100',
    green: 'text-green-600 bg-green-100',
    yellow: 'text-yellow-600 bg-yellow-100',
    purple: 'text-purple-600 bg-purple-100',
    red: 'text-red-600 bg-red-100',
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
                <div className={`ml-2 flex items-baseline text-sm font-semibold ${
                  trend === 'up' ? 'text-green-600' : 'text-red-600'
                }`}>
                  <TrendingUpIcon className={`self-center flex-shrink-0 h-4 w-4 ${
                    trend === 'down' ? 'rotate-180' : ''
                  }`} />
                  <span className="sr-only">
                    {trend === 'up' ? 'Increased' : 'Decreased'} by
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
  const { data: dashboardData, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: async () => {
      // Since we don't have a specific dashboard endpoint, we'll fetch basic data
      const [clients, orders, courses, classes] = await Promise.all([
        api.get('/clients').catch(() => ({ data: [] })),
        api.get('/orders').catch(() => ({ data: [] })),
        api.get('/courses').catch(() => ({ data: [] })),
        api.get('/classes').catch(() => ({ data: [] })),
      ]);

      return {
        clients: clients.data || [],
        orders: orders.data || [],
        courses: courses.data || [],
        classes: classes.data || [],
      };
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  if (isLoading) {
    return <LoadingPage message="Loading dashboard..." />;
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 text-lg font-semibold mb-2">Error loading dashboard</div>
        <p className="text-gray-600">Please try refreshing the page</p>
      </div>
    );
  }

  const stats = [
    {
      title: 'Total Clients',
      value: dashboardData?.clients?.length || 0,
      icon: UsersIcon,
      color: 'blue',
      trend: 'up',
      trendValue: '12%',
    },
    {
      title: 'Active Orders',
      value: dashboardData?.orders?.filter(order => order.status === 'active')?.length || 0,
      icon: ShoppingBagIcon,
      color: 'green',
      trend: 'up',
      trendValue: '8%',
    },
    {
      title: 'Available Courses',
      value: dashboardData?.courses?.length || 0,
      icon: AcademicCapIcon,
      color: 'purple',
    },
    {
      title: 'Scheduled Classes',
      value: dashboardData?.classes?.length || 0,
      icon: CalendarIcon,
      color: 'yellow',
      trend: 'up',
      trendValue: '4%',
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

      {/* Recent Activity */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <Card.Header>
            <Card.Title>Recent Clients</Card.Title>
          </Card.Header>
          <Card.Content>
            {dashboardData?.clients?.length > 0 ? (
              <div className="space-y-3">
                {dashboardData.clients.slice(0, 5).map((client, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-gray-600">
                        {client.name?.charAt(0) || 'C'}
                      </span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {client.name || 'Unknown Client'}
                      </p>
                      <p className="text-sm text-gray-500 truncate">
                        {client.email || 'No email'}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No clients yet</p>
            )}
          </Card.Content>
        </Card>

        <Card>
          <Card.Header>
            <Card.Title>Recent Orders</Card.Title>
          </Card.Header>
          <Card.Content>
            {dashboardData?.orders?.length > 0 ? (
              <div className="space-y-3">
                {dashboardData.orders.slice(0, 5).map((order, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        Order #{order.id || index + 1}
                      </p>
                      <p className="text-sm text-gray-500">
                        {order.status || 'pending'}
                      </p>
                    </div>
                    <div className="flex-shrink-0 text-sm font-medium text-gray-900">
                      ${order.total || '0.00'}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No orders yet</p>
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
              <span className="text-sm font-medium text-blue-900">Add Client</span>
            </button>
            <button className="flex items-center p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors">
              <ShoppingBagIcon className="h-6 w-6 text-green-600 mr-3" />
              <span className="text-sm font-medium text-green-900">Create Order</span>
            </button>
            <button className="flex items-center p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors">
              <AcademicCapIcon className="h-6 w-6 text-purple-600 mr-3" />
              <span className="text-sm font-medium text-purple-900">Add Course</span>
            </button>
            <button className="flex items-center p-4 bg-yellow-50 rounded-lg hover:bg-yellow-100 transition-colors">
              <CalendarIcon className="h-6 w-6 text-yellow-600 mr-3" />
              <span className="text-sm font-medium text-yellow-900">Schedule Class</span>
            </button>
          </div>
        </Card.Content>
      </Card>
    </div>
  );
};

export default Dashboard;
