import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../context/AuthContext';
import { carAPI, workOrderAPI, appointmentAPI, customerAPI } from '../../services/api';
import { format } from 'date-fns';

const CustomerDashboard = () => {
  const { t } = useTranslation();
  const { logout } = useAuth();
  
  const [cars, setCars] = useState([]);
  const [workOrders, setWorkOrders] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [customer, setCustomer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showAppointmentForm, setShowAppointmentForm] = useState(false);
  const [appointmentForm, setAppointmentForm] = useState({
    carId: '',
    unregisteredCarDetails: '',
    issueDescription: '',
    preferredDate: '',
    preferredTime: '',
  });
  const [appointmentError, setAppointmentError] = useState('');
  const [appointmentSubmitting, setAppointmentSubmitting] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [carsRes, workOrdersRes, appointmentsRes, customerRes] = await Promise.all([
        carAPI.getMyCars(),
        workOrderAPI.list({ limit: 5 }),
        appointmentAPI.list({ limit: 5 }),
        customerAPI.getMe()
      ]);
      
      setCars(carsRes.data);
      setWorkOrders(workOrdersRes.data);
      setAppointments(appointmentsRes.data);
      setCustomer(customerRes.data);
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

  const handleAppointmentChange = (field, value) => {
    setAppointmentForm((prev) => ({ ...prev, [field]: value }));
  };

  const resetAppointmentForm = () => {
    setAppointmentForm({
      carId: '',
      unregisteredCarDetails: '',
      issueDescription: '',
      preferredDate: '',
      preferredTime: '',
    });
  };

  const handleCreateAppointment = async (event) => {
    event.preventDefault();
    if (!customer) {
      setAppointmentError(t('error'));
      return;
    }

    setAppointmentError('');
    setAppointmentSubmitting(true);

    const isNewCar = appointmentForm.carId === 'new';
    const hasCarId = appointmentForm.carId && !isNewCar;

    const payload = {
      shop_id: customer.shop_id,
      customer_id: customer.id,
      car_id: hasCarId ? Number(appointmentForm.carId) : null,
      unregistered_car_details: isNewCar
        ? appointmentForm.unregisteredCarDetails || null
        : null,
      issue_description: appointmentForm.issueDescription,
      preferred_date: new Date(appointmentForm.preferredDate).toISOString(),
      preferred_time: appointmentForm.preferredTime || null,
    };

    try {
      await appointmentAPI.create(payload);
      await loadData();
      resetAppointmentForm();
      setShowAppointmentForm(false);
    } catch (error) {
      setAppointmentError(error.response?.data?.detail || t('error'));
    } finally {
      setAppointmentSubmitting(false);
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
            <button
              className="btn btn-primary"
              onClick={() => setShowAppointmentForm(true)}
            >
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

      {showAppointmentForm && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-lg w-full max-w-lg p-6">
            <h4 className="text-lg font-semibold mb-4">{t('bookAppointment')}</h4>
            <form onSubmit={handleCreateAppointment} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('cars')}
                </label>
                <select
                  className="input"
                  value={appointmentForm.carId}
                  onChange={(event) => handleAppointmentChange('carId', event.target.value)}
                  required
                >
                  <option value="">{t('selectCar')}</option>
                  {cars.map((car) => (
                    <option key={car.id} value={car.id}>
                      {car.make} {car.model} ({car.license_plate})
                    </option>
                  ))}
                  <option value="new">{t('newCar')}</option>
                </select>
              </div>

              {appointmentForm.carId === 'new' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {t('carDetails')}
                  </label>
                  <input
                    type="text"
                    className="input"
                    value={appointmentForm.unregisteredCarDetails}
                    onChange={(event) =>
                      handleAppointmentChange('unregisteredCarDetails', event.target.value)
                    }
                    placeholder={t('carDetailsPlaceholder')}
                    required
                  />
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('reportedIssues')}
                </label>
                <textarea
                  className="input min-h-[96px]"
                  value={appointmentForm.issueDescription}
                  onChange={(event) =>
                    handleAppointmentChange('issueDescription', event.target.value)
                  }
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('preferredDate')}
                </label>
                <input
                  type="datetime-local"
                  className="input"
                  value={appointmentForm.preferredDate}
                  onChange={(event) =>
                    handleAppointmentChange('preferredDate', event.target.value)
                  }
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('preferredTime')}
                </label>
                <input
                  type="text"
                  className="input"
                  value={appointmentForm.preferredTime}
                  onChange={(event) =>
                    handleAppointmentChange('preferredTime', event.target.value)
                  }
                  placeholder="09:00"
                />
              </div>

              {appointmentError && (
                <div className="bg-red-50 text-red-600 p-3 rounded-md text-sm">
                  {appointmentError}
                </div>
              )}

              <div className="flex justify-end gap-3">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setShowAppointmentForm(false);
                    setAppointmentError('');
                  }}
                >
                  {t('cancel')}
                </button>
                <button type="submit" className="btn btn-primary" disabled={appointmentSubmitting}>
                  {appointmentSubmitting ? t('loading') : t('submit')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default CustomerDashboard;
