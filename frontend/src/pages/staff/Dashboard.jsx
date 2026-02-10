import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { format } from 'date-fns';
import StaffLayout from '../../components/StaffLayout';
import { reportsAPI, workOrderAPI, appointmentAPI } from '../../services/api';

const StaffDashboard = () => {
  const { t } = useTranslation();
  
  const [stats, setStats] = useState(null);
  const [workOrders, setWorkOrders] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [statsRes, workOrdersRes, appointmentsRes] = await Promise.all([
        reportsAPI.getDashboard(),
        workOrderAPI.list({ limit: 10 }),
        appointmentAPI.getPending()
      ]);
      
      setStats(statsRes.data);
      setWorkOrders(workOrdersRes.data);
      setAppointments(appointmentsRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async (appointmentId, preferredDate) => {
    try {
      await appointmentAPI.update(appointmentId, {
        status: 'confirmed',
        confirmed_date: preferredDate,
      });
      await loadData();
    } catch (error) {
      console.error('Error confirming appointment:', error);
    }
  };

  const handleReject = async (appointmentId) => {
    const reason = window.prompt('Reason for rejection?');
    if (reason === null) {
      return;
    }
    try {
      await appointmentAPI.update(appointmentId, {
        status: 'rejected',
        rejection_reason: reason || null,
      });
      await loadData();
    } catch (error) {
      console.error('Error rejecting appointment:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">{t('loading')}</div>
      </div>
    );
  }

  return (
    <StaffLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-gray-600">
            Welcome back! Here's what's happening today.
          </p>
        </div>
        {/* Stats Grid */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="card">
              <h3 className="text-sm font-medium text-gray-500 mb-2">
                Total Customers
              </h3>
              <p className="text-3xl font-bold text-primary-600">
                {stats.total_customers}
              </p>
            </div>
            
            <div className="card">
              <h3 className="text-sm font-medium text-gray-500 mb-2">
                Active Work Orders
              </h3>
              <p className="text-3xl font-bold text-yellow-600">
                {stats.active_work_orders}
              </p>
            </div>
            
            <div className="card">
              <h3 className="text-sm font-medium text-gray-500 mb-2">
                Revenue Today
              </h3>
              <p className="text-3xl font-bold text-green-600">
                {stats.revenue_today.toFixed(2)}
              </p>
              <p className="text-xs text-gray-500 mt-1">лв</p>
            </div>
            
            <div className="card">
              <h3 className="text-sm font-medium text-gray-500 mb-2">
                Pending Appointments
              </h3>
              <p className="text-3xl font-bold text-blue-600">
                {stats.pending_appointments}
              </p>
            </div>
          </div>
        )}

        {/* Pending Appointments */}
        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            Pending Appointments
          </h3>
          
          <div className="card">
            {appointments.length === 0 ? (
              <p className="text-gray-500 text-center py-4">
                No pending appointments
              </p>
            ) : (
              <div className="space-y-4">
                {appointments.map((apt) => (
                  <div key={apt.id} className="border-b border-gray-200 last:border-0 pb-4 last:pb-0">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-medium">
                          {apt.customer?.first_name} {apt.customer?.last_name}
                        </h4>
                        <p className="text-sm text-gray-600 mt-1">
                          {apt.issue_description}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          Preferred: {format(new Date(apt.preferred_date), 'dd.MM.yyyy HH:mm')}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <button
                          className="btn btn-primary text-sm"
                          onClick={() => handleConfirm(apt.id, apt.preferred_date)}
                        >
                          Confirm
                        </button>
                        <button
                          className="btn btn-danger text-sm"
                          onClick={() => handleReject(apt.id)}
                        >
                          Reject
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Recent Work Orders */}
        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            Recent Work Orders
          </h3>
          
          <div className="card overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Customer
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Car
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Issue
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Mechanic
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {workOrders.map((wo) => (
                  <tr key={wo.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm">
                      {wo.customer?.first_name} {wo.customer?.last_name}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      {wo.car?.make} {wo.car?.model}
                    </td>
                    <td className="px-4 py-3 text-sm max-w-xs truncate">
                      {wo.reported_issues}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span className={`badge badge-${
                        wo.status === 'done' ? 'success' :
                        wo.status === 'in_progress' ? 'warning' : 'info'
                      }`}>
                        {wo.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      {wo.assigned_mechanic?.first_name} {wo.assigned_mechanic?.last_name}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </StaffLayout>
  );
};

export default StaffDashboard;
