import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { 
  PlusIcon, 
  MagnifyingGlassIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon
} from '@heroicons/react/24/outline';
import { Card, Button, Input, Table, Modal, LoadingPage } from '../components/ui';
import { api } from '../services/api';
import { useDebounce } from '../hooks';

const ClientForm = ({ client, isOpen, onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    name: client?.name || '',
    email: client?.email || '',
    phone: client?.phone || '',
    date_of_birth: client?.date_of_birth || '',
    emergency_contact: client?.emergency_contact || '',
    medical_conditions: client?.medical_conditions || '',
    fitness_goals: client?.fitness_goals || '',
    ...client
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

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={client ? 'Edit Client' : 'Add New Client'} size="lg">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Input
            label="Name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
          />
          <Input
            label="Email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            required
          />
          <Input
            label="Phone"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
          />
          <Input
            label="Date of Birth"
            name="date_of_birth"
            type="date"
            value={formData.date_of_birth}
            onChange={handleChange}
          />
        </div>
        
        <Input
          label="Emergency Contact"
          name="emergency_contact"
          value={formData.emergency_contact}
          onChange={handleChange}
        />
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Medical Conditions
            </label>
            <textarea
              name="medical_conditions"
              rows={3}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              placeholder="Any medical conditions or limitations..."
              value={formData.medical_conditions}
              onChange={handleChange}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Fitness Goals
            </label>
            <textarea
              name="fitness_goals"
              rows={3}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              placeholder="Client's fitness goals and objectives..."
              value={formData.fitness_goals}
              onChange={handleChange}
            />
          </div>
        </div>

        <div className="flex justify-end space-x-3 pt-4">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit">
            {client ? 'Update Client' : 'Add Client'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};

const Clients = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingClient, setEditingClient] = useState(null);
  const debouncedSearchTerm = useDebounce(searchTerm, 300);
  const queryClient = useQueryClient();

  const { data: clients = [], isLoading, error } = useQuery({
    queryKey: ['clients', debouncedSearchTerm],
    queryFn: async () => {
      const response = await api.get('/clients', {
        params: debouncedSearchTerm ? { search: debouncedSearchTerm } : {}
      });
      return response.data;
    },
  });

  const createClientMutation = useMutation({
    mutationFn: (clientData) => api.post('/clients', clientData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      setIsModalOpen(false);
      setEditingClient(null);
    },
  });

  const updateClientMutation = useMutation({
    mutationFn: ({ id, ...clientData }) => api.put(`/clients/${id}`, clientData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      setIsModalOpen(false);
      setEditingClient(null);
    },
  });

  const deleteClientMutation = useMutation({
    mutationFn: (clientId) => api.delete(`/clients/${clientId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
    },
  });

  const handleAddClient = () => {
    setEditingClient(null);
    setIsModalOpen(true);
  };

  const handleEditClient = (client) => {
    setEditingClient(client);
    setIsModalOpen(true);
  };

  const handleDeleteClient = async (clientId) => {
    if (window.confirm('Are you sure you want to delete this client?')) {
      deleteClientMutation.mutate(clientId);
    }
  };

  const handleSubmitClient = (clientData) => {
    if (editingClient) {
      updateClientMutation.mutate({ ...clientData, id: editingClient.id });
    } else {
      createClientMutation.mutate(clientData);
    }
  };

  const columns = [
    {
      header: 'Name',
      accessor: 'name',
    },
    {
      header: 'Email',
      accessor: 'email',
    },
    {
      header: 'Phone',
      accessor: 'phone',
    },
    {
      header: 'Fitness Goals',
      cell: (client) => (
        <div className="max-w-xs truncate">
          {client.fitness_goals || 'Not specified'}
        </div>
      ),
    },
    {
      header: 'Actions',
      cell: (client) => (
        <div className="flex space-x-2">
          <Link
            to={`/clients/${client.id}`}
            className="text-blue-600 hover:text-blue-900"
          >
            <EyeIcon className="h-4 w-4" />
          </Link>
          <button
            onClick={() => handleEditClient(client)}
            className="text-green-600 hover:text-green-900"
          >
            <PencilIcon className="h-4 w-4" />
          </button>
          <button
            onClick={() => handleDeleteClient(client.id)}
            className="text-red-600 hover:text-red-900"
          >
            <TrashIcon className="h-4 w-4" />
          </button>
        </div>
      ),
    },
  ];

  if (isLoading) {
    return <LoadingPage message="Loading clients..." />;
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 text-lg font-semibold mb-2">Error loading clients</div>
        <p className="text-gray-600">Please try refreshing the page</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Clients</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage your fitness studio clients
          </p>
        </div>
        <Button onClick={handleAddClient}>
          <PlusIcon className="h-4 w-4 mr-2" />
          Add Client
        </Button>
      </div>

      <Card className="p-6">
        <div className="mb-4">
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search clients..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        <Table columns={columns} data={clients} />
      </Card>

      <ClientForm
        client={editingClient}
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setEditingClient(null);
        }}
        onSubmit={handleSubmitClient}
      />
    </div>
  );
};

export default Clients;
