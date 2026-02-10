import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { format } from 'date-fns';
import StaffLayout from '../../components/StaffLayout';
import { workOrderAPI } from '../../services/api';

const WorkOrders = () => {
  const { t } = useTranslation();
  const [workOrders, setWorkOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    loadWorkOrders();
  }, []);

  const loadWorkOrders = async () => {
    try {
      const response = await workOrderAPI.list();
      setWorkOrders(response.data);
    } catch (error) {
      console.error('Error loading work orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusClasses = {
      created: 'badge-info',
      diagnosing: 'badge-warning',
      in_progress: 'badge-warning',
      done: 'badge-success',
    };
    
    return (
      <span className={`badge ${statusClasses[status] || 'badge-info'}`}>
        {status.replace('_', ' ').toUpperCase()}
      </span>
    );
  };

  const filteredWorkOrders = statusFilter === 'all'
    ? workOrders
    : workOrders.filter(wo => wo.status === statusFilter);

  const statusCounts = {
    all: workOrders.length,
    created: workOrders.filter(wo => wo.status === 'created').length,
    diagnosing: workOrders.filter(wo => wo.status === 'diagnosing').length,
    in_progress: workOrders.filter(wo => wo.status === 'in_progress').length,
    done: workOrders.filter(wo => wo.status === 'done').length,
  };

  if (loading) {
    return (
      <StaffLayout>
        <div className="flex items-center justify-center min-h-96">
          <div className="text-lg">{t('loading')}</div>
        </div>
      </StaffLayout>
    );
  }

  return (
    <StaffLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Work Orders</h1>
            <p className="mt-2 text-gray-600">
              Manage and track all work orders
            </p>
          </div>
          <button className="btn btn-primary">
            + Create Work Order
          </button>
        </div>

        {/* Status filters */}
        <div className="card">
          <div className="flex flex-wrap gap-2">
            {Object.entries(statusCounts).map(([status, count]) => (
              <button
                key={status}
                onClick={() => setStatusFilter(status)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  statusFilter === status
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {status === 'all' ? 'All' : status.replace('_', ' ').toUpperCase()} ({count})
              </button>
            ))}
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Total Work Orders
            </h3>
            <p className="text-3xl font-bold text-primary-600">
              {workOrders.length}
            </p>
          </div>
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              In Progress
            </h3>
            <p className="text-3xl font-bold text-yellow-600">
              {statusCounts.in_progress + statusCounts.diagnosing}
            </p>
          </div>
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Completed
            </h3>
            <p className="text-3xl font-bold text-green-600">
              {statusCounts.done}
            </p>
          </div>
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Pending
            </h3>
            <p className="text-3xl font-bold text-blue-600">
              {statusCounts.created}
            </p>
          </div>
        </div>

        {/* Work Orders table */}
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Customer
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Vehicle
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Issue
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Mechanic
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredWorkOrders.length === 0 ? (
                  <tr>
                    <td colSpan="8" className="px-6 py-8 text-center text-gray-500">
                      No work orders found
                    </td>
                  </tr>
                ) : (
                  filteredWorkOrders.map((wo) => (
                    <tr key={wo.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm font-medium text-gray-900">
                          #{wo.id}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-8 w-8 bg-primary-100 rounded-full flex items-center justify-center">
                            <span className="text-primary-700 text-xs font-semibold">
                              {wo.customer?.first_name?.[0]}{wo.customer?.last_name?.[0]}
                            </span>
                          </div>
                          <div className="ml-3">
                            <div className="text-sm font-medium text-gray-900">
                              {wo.customer?.first_name} {wo.customer?.last_name}
                            </div>
                            <div className="text-sm text-gray-500">
                              {wo.customer?.phone}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {wo.car?.make} {wo.car?.model}
                        </div>
                        <div className="text-sm text-gray-500">
                          {wo.car?.license_plate}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900 max-w-xs truncate">
                          {wo.reported_issues}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {wo.assigned_mechanic ? (
                          <div className="text-sm text-gray-900">
                            {wo.assigned_mechanic.first_name} {wo.assigned_mechanic.last_name}
                          </div>
                        ) : (
                          <span className="text-sm text-gray-400 italic">
                            Unassigned
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(wo.status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-900">
                          {format(new Date(wo.created_at), 'dd.MM.yyyy')}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <Link
                          to={`/work-orders/${wo.id}`}
                          className="text-primary-600 hover:text-primary-900"
                        >
                          View
                        </Link>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </StaffLayout>
  );
};

export default WorkOrders;
