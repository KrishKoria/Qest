import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { 
  PlusIcon, 
  MagnifyingGlassIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { Card, Button, Input, Table, Modal, Select, LoadingPage } from '../components/ui';
import { api } from '../services/api';
import { useDebounce } from '../hooks';
import { formatDate, formatCurrency } from '../utils';

const statusColors = {
  pending: 'bg-yellow-100 text-yellow-800',
  confirmed: 'bg-blue-100 text-blue-800',
  active: 'bg-green-100 text-green-800',
  completed: 'bg-gray-100 text-gray-800',
  cancelled: 'bg-red-100 text-red-800',
};

const statusIcons = {
  pending: ClockIcon,
  confirmed: CheckCircleIcon,
  active: CheckCircleIcon,
  completed: CheckCircleIcon,
  cancelled: XCircleIcon,
};

const StatusBadge = ({ status }) => {
  const Icon = statusIcons[status] || ClockIcon;
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColors[status]}`}>
      <Icon className="w-3 h-3 mr-1" />
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
};

const OrderForm = ({ order, isOpen, onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    client_id: order?.client_id || '',
    service_type: order?.service_type || '',
    description: order?.description || '',
    total: order?.total || '',
    status: order?.status || 'pending',
    scheduled_date: order?.scheduled_date || '',
    notes: order?.notes || '',
    ...order
  });

  const { data: clients = [] } = useQuery({
    queryKey: ['clients'],
    queryFn: async () => {
      const response = await api.get('/clients');
      return response.data;
    },
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const serviceTypes = [
    { value: 'personal_training', label: 'Personal Training' },
    { value: 'group_class', label: 'Group Class' },
    { value: 'nutrition_consultation', label: 'Nutrition Consultation' },
    { value: 'fitness_assessment', label: 'Fitness Assessment' },
    { value: 'program_design', label: 'Program Design' },
  ];

  const statusOptions = [
    { value: 'pending', label: 'Pending' },
    { value: 'confirmed', label: 'Confirmed' },
    { value: 'active', label: 'Active' },
    { value: 'completed', label: 'Completed' },
    { value: 'cancelled', label: 'Cancelled' },
  ];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={order ? 'Edit Order' : 'Create New Order'} size="lg">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Select
            label="Client"
            name="client_id"
            value={formData.client_id}
            onChange={handleChange}
            options={clients.map(client => ({ value: client.id, label: client.name }))}
            required
          />
          <Select
            label="Service Type"
            name="service_type"
            value={formData.service_type}
            onChange={handleChange}
            options={serviceTypes}
            required
          />
          <Input
            label="Total Amount"
            name="total"
            type="number"
            step="0.01"
            value={formData.total}
            onChange={handleChange}
            required
          />
          <Select
            label="Status"
            name="status"
            value={formData.status}
            onChange={handleChange}
            options={statusOptions}
            required
          />
          <Input
            label="Scheduled Date"
            name="scheduled_date"
            type="datetime-local"
            value={formData.scheduled_date}
            onChange={handleChange}
          />
        </div>
        
        <Input
          label="Description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder="Brief description of the service..."
        />
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Notes
          </label>
          <textarea
            name="notes"
            rows={3}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            placeholder="Additional notes or special instructions..."
            value={formData.notes}
            onChange={handleChange}
          />
        </div>

        <div className="flex justify-end space-x-3 pt-4">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit">
            {order ? 'Update Order' : 'Create Order'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};

const Orders = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingOrder, setEditingOrder] = useState(null);
  const debouncedSearchTerm = useDebounce(searchTerm, 300);
  const queryClient = useQueryClient();

  const { data: orders = [], isLoading, error } = useQuery({
    queryKey: ['orders', debouncedSearchTerm, statusFilter],
    queryFn: async () => {
      const params = {};
      if (debouncedSearchTerm) params.search = debouncedSearchTerm;
      if (statusFilter) params.status = statusFilter;
      
      const response = await api.get('/orders', { params });
      return response.data;
    },
  });

  const { data: clients = [] } = useQuery({
    queryKey: ['clients'],
    queryFn: async () => {
      const response = await api.get('/clients');
      return response.data;
    },
  });

  const createOrderMutation = useMutation({
    mutationFn: (orderData) => api.post('/orders', orderData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
      setIsModalOpen(false);
      setEditingOrder(null);
    },
  });

  const updateOrderMutation = useMutation({
    mutationFn: ({ id, ...orderData }) => api.put(`/orders/${id}`, orderData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
      setIsModalOpen(false);
      setEditingOrder(null);
    },
  });

  const deleteOrderMutation = useMutation({
    mutationFn: (orderId) => api.delete(`/orders/${orderId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
    },
  });

  const handleAddOrder = () => {
    setEditingOrder(null);
    setIsModalOpen(true);
  };

  const handleEditOrder = (order) => {
    setEditingOrder(order);
    setIsModalOpen(true);
  };

  const handleDeleteOrder = async (orderId) => {
    if (window.confirm('Are you sure you want to delete this order?')) {
      deleteOrderMutation.mutate(orderId);
    }
  };

  const handleSubmitOrder = (orderData) => {
    if (editingOrder) {
      updateOrderMutation.mutate({ ...orderData, id: editingOrder.id });
    } else {
      createOrderMutation.mutate(orderData);
    }
  };

  const getClientName = (clientId) => {
    const client = clients.find(c => c.id === clientId);
    return client ? client.name : 'Unknown Client';
  };

  const columns = [
    {
      header: 'Order ID',
      accessor: 'id',
      cell: (order) => `#${order.id}`,
    },
    {
      header: 'Client',
      cell: (order) => getClientName(order.client_id),
    },
    {
      header: 'Service',
      accessor: 'service_type',
      cell: (order) => order.service_type?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'N/A',
    },
    {
      header: 'Total',
      accessor: 'total',
      cell: (order) => formatCurrency(order.total),
    },
    {
      header: 'Status',
      accessor: 'status',
      cell: (order) => <StatusBadge status={order.status} />,
    },
    {
      header: 'Scheduled Date',
      accessor: 'scheduled_date',
      cell: (order) => order.scheduled_date ? formatDate(order.scheduled_date) : 'Not scheduled',
    },
    {
      header: 'Actions',
      cell: (order) => (
        <div className="flex space-x-2">
          <Link
            to={`/orders/${order.id}`}
            className="text-blue-600 hover:text-blue-900"
          >
            <EyeIcon className="h-4 w-4" />
          </Link>
          <button
            onClick={() => handleEditOrder(order)}
            className="text-green-600 hover:text-green-900"
          >
            <PencilIcon className="h-4 w-4" />
          </button>
          <button
            onClick={() => handleDeleteOrder(order.id)}
            className="text-red-600 hover:text-red-900"
          >
            <TrashIcon className="h-4 w-4" />
          </button>
        </div>
      ),
    },
  ];

  const statusOptions = [
    { value: '', label: 'All Statuses' },
    { value: 'pending', label: 'Pending' },
    { value: 'confirmed', label: 'Confirmed' },
    { value: 'active', label: 'Active' },
    { value: 'completed', label: 'Completed' },
    { value: 'cancelled', label: 'Cancelled' },
  ];

  if (isLoading) {
    return <LoadingPage message="Loading orders..." />;
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 text-lg font-semibold mb-2">Error loading orders</div>
        <p className="text-gray-600">Please try refreshing the page</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Orders</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage client orders and service bookings
          </p>
        </div>
        <Button onClick={handleAddOrder}>
          <PlusIcon className="h-4 w-4 mr-2" />
          Create Order
        </Button>
      </div>

      <Card className="p-6">
        <div className="mb-4 flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search orders..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          <div className="w-full sm:w-48">
            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              options={statusOptions}
              placeholder="Filter by status"
            />
          </div>
        </div>

        <Table columns={columns} data={orders} />
      </Card>

      <OrderForm
        order={editingOrder}
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setEditingOrder(null);
        }}
        onSubmit={handleSubmitOrder}
      />
    </div>
  );
};

export default Orders;
