import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { format } from 'date-fns';
import StaffLayout from '../../components/StaffLayout';
import { smsLogAPI } from '../../services/api';

const SMSLogs = () => {
  const { t } = useTranslation();
  const [smsLogs, setSmsLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    message_type: '',
    status: '',
    recipient_phone: ''
  });

  useEffect(() => {
    loadSMSLogs();
  }, []);

  const loadSMSLogs = async () => {
    try {
      const params = {};
      if (filters.message_type) params.message_type = filters.message_type;
      if (filters.status) params.status = filters.status;
      if (filters.recipient_phone) params.recipient_phone = filters.recipient_phone;
      
      const response = await smsLogAPI.list(params);
      setSmsLogs(response.data);
    } catch (error) {
      console.error('Error loading SMS logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters({ ...filters, [key]: value });
  };

  const applyFilters = () => {
    setLoading(true);
    loadSMSLogs();
  };

  const clearFilters = () => {
    setFilters({
      message_type: '',
      status: '',
      recipient_phone: ''
    });
    setLoading(true);
    setTimeout(() => loadSMSLogs(), 100);
  };

  const getStatusBadge = (status) => {
    const statusClasses = {
      sent: 'badge-info',
      delivered: 'badge-success',
      failed: 'badge-error',
    };
    
    return (
      <span className={`badge ${statusClasses[status] || 'badge-info'}`}>
        {status?.toUpperCase() || 'UNKNOWN'}
      </span>
    );
  };

  const getMessageTypeLabel = (type) => {
    const labels = {
      welcome: 'Welcome',
      appointment_confirmed: 'Appointment Confirmed',
      car_ready: 'Car Ready',
      service_reminder: 'Service Reminder',
    };
    return labels[type] || type;
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
            <h1 className="text-3xl font-bold text-gray-900">SMS Logs</h1>
            <p className="mt-2 text-gray-600">
              View SMS messages sent to customers
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Filters</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Message Type
              </label>
              <select
                value={filters.message_type}
                onChange={(e) => handleFilterChange('message_type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="">All Types</option>
                <option value="welcome">Welcome</option>
                <option value="appointment_confirmed">Appointment Confirmed</option>
                <option value="car_ready">Car Ready</option>
                <option value="service_reminder">Service Reminder</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Status
              </label>
              <select
                value={filters.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="">All Statuses</option>
                <option value="sent">Sent</option>
                <option value="delivered">Delivered</option>
                <option value="failed">Failed</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Recipient Phone
              </label>
              <input
                type="text"
                value={filters.recipient_phone}
                onChange={(e) => handleFilterChange('recipient_phone', e.target.value)}
                placeholder="+359..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          </div>
          <div className="flex gap-2 mt-4">
            <button onClick={applyFilters} className="btn btn-primary">
              Apply Filters
            </button>
            <button onClick={clearFilters} className="btn">
              Clear Filters
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Total SMS
            </h3>
            <p className="text-3xl font-bold text-primary-600">
              {smsLogs.length}
            </p>
          </div>
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Delivered
            </h3>
            <p className="text-3xl font-bold text-green-600">
              {smsLogs.filter(log => log.status === 'delivered').length}
            </p>
          </div>
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Sent
            </h3>
            <p className="text-3xl font-bold text-blue-600">
              {smsLogs.filter(log => log.status === 'sent').length}
            </p>
          </div>
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Failed
            </h3>
            <p className="text-3xl font-bold text-red-600">
              {smsLogs.filter(log => log.status === 'failed').length}
            </p>
          </div>
        </div>

        {/* SMS Logs table */}
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date/Time
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Recipient
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Message
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {smsLogs.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="px-6 py-8 text-center text-gray-500">
                      No SMS logs found
                    </td>
                  </tr>
                ) : (
                  smsLogs.map((log) => (
                    <tr key={log.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-900">
                          {format(new Date(log.sent_at), 'dd.MM.yyyy')}
                        </span>
                        <div className="text-xs text-gray-500">
                          {format(new Date(log.sent_at), 'HH:mm:ss')}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm font-medium text-gray-900">
                          {log.recipient_phone}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-700">
                          {getMessageTypeLabel(log.message_type)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(log.status)}
                        {log.error_message && (
                          <div className="text-xs text-red-600 mt-1 max-w-xs truncate">
                            {log.error_message}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900 max-w-md truncate">
                          {log.message_body}
                        </div>
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

export default SMSLogs;
