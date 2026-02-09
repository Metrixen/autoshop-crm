import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../context/AuthContext';
import { carAPI, workOrderAPI, appointmentAPI } from '../../services/api';
import { format } from 'date-fns';

const CustomerDashboard = () => {
  const { t } = useTranslation();
  const { logout } = useAuth();
  
  const [cars, setCars] = useState([]);
  const [workOrders, setWorkOrders] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [carsRes, workOrdersRes, appointmentsRes] = await Promise.all([
        carAPI.getMyCars(),
        workOrderAPI.list({ limit: 5 }),
        appointmentAPI.list({ limit: 5 })
      ]);
      
      setCars(carsRes.data);
      setWorkOrders(workOrdersRes.data);
      setAppointments(appointmentsRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
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
      requested: 'badge-info',
      confirmed: 'badge-success',
    };
    
    return (
      <span className={`badge ${statusClasses[status] || 'badge-info'}`}>
        {t(`status.${status}`)}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">{t('loading')}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">
              AutoShop CRM
            </h1>
            <button onClick={logout} className="btn btn-secondary">
              {t('logout')}
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            {t('welcome')}
          </h2>
          <p className="text-gray-600">
            {t('dashboard')}
          </p>
        </div>

        {/* My Cars */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-semibold text-gray-900">
              {t('myCars')}
            </h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {cars.map((car) => (
              <div key={car.id} className="card">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-semibold text-lg">
                    {car.make} {car.model}
                  </h4>
                  <span className="text-sm text-gray-500">{car.year}</span>
                </div>
                <p className="text-gray-600 mb-2">{car.license_plate}</p>
                <p className="text-sm text-gray-500">
                  {car.current_mileage.toLocaleString()} km
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Active Work Orders */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            {t('workOrders')}
          </h3>
          
          <div className="card">
            {workOrders.length === 0 ? (
              <p className="text-gray-500 text-center py-4">
                No active work orders
              </p>
            ) : (
              <div className="space-y-4">
                {workOrders.map((wo) => (
                  <div key={wo.id} className="border-b border-gray-200 last:border-0 pb-4 last:pb-0">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h4 className="font-medium">
                          {wo.car?.make} {wo.car?.model} ({wo.car?.license_plate})
                        </h4>
                        <p className="text-sm text-gray-600 mt-1">
                          {wo.reported_issues}
                        </p>
                      </div>
                      {getStatusBadge(wo.status)}
                    </div>
                    <p className="text-xs text-gray-500">
                      {format(new Date(wo.created_at), 'dd.MM.yyyy HH:mm')}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* My Appointments */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-semibold text-gray-900">
              {t('myAppointments')}
            </h3>
            <button className="btn btn-primary">
              {t('bookAppointment')}
            </button>
          </div>
          
          <div className="card">
            {appointments.length === 0 ? (
              <p className="text-gray-500 text-center py-4">
                No appointments scheduled
              </p>
            ) : (
              <div className="space-y-4">
                {appointments.map((apt) => (
                  <div key={apt.id} className="border-b border-gray-200 last:border-0 pb-4 last:pb-0">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h4 className="font-medium">
                          {format(new Date(apt.preferred_date), 'dd.MM.yyyy HH:mm')}
                        </h4>
                        <p className="text-sm text-gray-600 mt-1">
                          {apt.issue_description}
                        </p>
                      </div>
                      {getStatusBadge(apt.status)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default CustomerDashboard;
