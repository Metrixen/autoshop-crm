import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../context/AuthContext';
import { carAPI, workOrderAPI, appointmentAPI, customerAPI, invoiceAPI } from '../../services/api';
import { format } from 'date-fns';

const CustomerDashboard = () => {
  const { t } = useTranslation();
  const { logout } = useAuth();
  
  const [cars, setCars] = useState([]);
  const [workOrders, setWorkOrders] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [customer, setCustomer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedVehicle, setSelectedVehicle] = useState(null);
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
      const [carsRes, workOrdersRes, appointmentsRes, customerRes, invoicesRes] = await Promise.all([
        carAPI.getMyCars(),
        workOrderAPI.list({ limit: 10 }),
        appointmentAPI.list({ limit: 10 }),
        customerAPI.getMe(),
        invoiceAPI.list({ limit: 10 })
      ]);
      
      setCars(carsRes.data);
      setWorkOrders(workOrdersRes.data);
      setAppointments(appointmentsRes.data);
      setCustomer(customerRes.data);
      setInvoices(invoicesRes.data);
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
      rejected: 'badge-danger',
      draft: 'badge-info',
      finalized: 'badge-warning',
      paid: 'badge-success',
    };
    
    return (
      <span className={`badge ${statusClasses[status] || 'badge-info'}`}>
        {status.replace('_', ' ').toUpperCase()}
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
            {t('welcome')}, {customer?.first_name}!
          </h2>
          <p className="text-gray-600">
            Manage your vehicles, track service history, and book appointments
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              My Vehicles
            </h3>
            <p className="text-3xl font-bold text-primary-600">
              {cars.length}
            </p>
          </div>
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Active Work Orders
            </h3>
            <p className="text-3xl font-bold text-yellow-600">
              {workOrders.filter(wo => wo.status !== 'done').length}
            </p>
          </div>
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Upcoming Appointments
            </h3>
            <p className="text-3xl font-bold text-blue-600">
              {appointments.filter(apt => apt.status !== 'rejected').length}
            </p>
          </div>
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Pending Invoices
            </h3>
            <p className="text-3xl font-bold text-green-600">
              {invoices.filter(inv => inv.status === 'finalized').length}
            </p>
          </div>
        </div>

        {/* My Cars */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-semibold text-gray-900">
              {t('myCars')}
            </h3>
            <button
              className="btn btn-primary"
              onClick={() => setShowAppointmentForm(true)}
            >
              📅 {t('bookAppointment')}
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {cars.length === 0 ? (
              <div className="col-span-full card text-center py-8">
                <p className="text-gray-500">No vehicles registered yet</p>
              </div>
            ) : (
              cars.map((car) => {
                const carWorkOrders = workOrders.filter(wo => wo.car_id === car.id);
                const lastService = carWorkOrders.length > 0 
                  ? carWorkOrders.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))[0]
                  : null;
                
                return (
                  <div 
                    key={car.id} 
                    className="card cursor-pointer hover:shadow-lg transition-shadow"
                    onClick={() => setSelectedVehicle(car)}
                  >
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h4 className="font-semibold text-lg text-gray-900">
                          {car.make} {car.model}
                        </h4>
                        <p className="text-sm text-gray-600">{car.year}</p>
                      </div>
                      <span className="text-2xl">🚗</span>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500">License Plate:</span>
                        <span className="font-medium text-gray-900">{car.license_plate}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500">Mileage:</span>
                        <span className="font-medium text-gray-900">{(car.current_mileage || 0).toLocaleString()} km</span>
                      </div>
                      {lastService && (
                        <div className="pt-2 mt-2 border-t border-gray-200">
                          <p className="text-xs text-gray-500">
                            Last service: {format(new Date(lastService.created_at), 'dd.MM.yyyy')}
                          </p>
                        </div>
                      )}
                    </div>
                    
                    <button 
                      className="mt-3 w-full btn btn-secondary text-sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedVehicle(car);
                      }}
                    >
                      View Details →
                    </button>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Active Work Orders */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            Service History & Active Work Orders
          </h3>
          
          <div className="card">
            {workOrders.length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                No service history available
              </p>
            ) : (
              <div className="space-y-4">
                {workOrders.map((wo) => (
                  <div key={wo.id} className="border-b border-gray-200 last:border-0 pb-4 last:pb-0">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h4 className="font-medium text-gray-900">
                            {wo.car?.make} {wo.car?.model} ({wo.car?.license_plate})
                          </h4>
                          {getStatusBadge(wo.status)}
                        </div>
                        <p className="text-sm text-gray-600">
                          {wo.reported_issues}
                        </p>
                        {wo.diagnostic_notes && (
                          <p className="text-sm text-gray-500 mt-1">
                            <span className="font-medium">Diagnosis:</span> {wo.diagnostic_notes}
                          </p>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between mt-3 text-sm">
                      <div className="flex items-center gap-4 text-gray-500">
                        <span>📅 {format(new Date(wo.created_at), 'dd.MM.yyyy HH:mm')}</span>
                        {wo.assigned_mechanic && (
                          <span>👨‍🔧 {wo.assigned_mechanic.first_name}</span>
                        )}
                        {wo.mileage_at_intake && (
                          <span>🛣️ {wo.mileage_at_intake.toLocaleString()} km</span>
                        )}
                      </div>
                      {wo.invoice && (
                        <span className="font-semibold text-green-600">
                          {wo.invoice.total.toFixed(2)} лв
                        </span>
                      )}
                    </div>
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
          </div>
          
          <div className="card">
            {appointments.length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                No appointments scheduled
              </p>
            ) : (
              <div className="space-y-4">
                {appointments.map((apt) => (
                  <div key={apt.id} className="border-b border-gray-200 last:border-0 pb-4 last:pb-0">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <div className="flex items-center gap-3 mb-1">
                          <h4 className="font-medium text-gray-900">
                            {format(new Date(apt.preferred_date), 'dd.MM.yyyy HH:mm')}
                          </h4>
                          {getStatusBadge(apt.status)}
                        </div>
                        <p className="text-sm text-gray-600">
                          {apt.issue_description}
                        </p>
                        {apt.rejection_reason && (
                          <p className="text-sm text-red-600 mt-1">
                            <span className="font-medium">Rejected:</span> {apt.rejection_reason}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* My Invoices */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            Invoices & Payments
          </h3>
          
          <div className="card">
            {invoices.length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                No invoices available
              </p>
            ) : (
              <div className="space-y-4">
                {invoices.map((invoice) => (
                  <div key={invoice.id} className="border-b border-gray-200 last:border-0 pb-4 last:pb-0">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h4 className="font-medium text-gray-900">
                            Invoice #{invoice.invoice_number}
                          </h4>
                          {getStatusBadge(invoice.status)}
                        </div>
                        <p className="text-sm text-gray-600">
                          {invoice.work_order?.car?.make} {invoice.work_order?.car?.model}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {format(new Date(invoice.created_at), 'dd.MM.yyyy')}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-gray-900">
                          {invoice.total.toFixed(2)} лв
                        </p>
                        <button
                          onClick={async () => {
                            try {
                              const response = await invoiceAPI.downloadPDF(invoice.id);
                              const url = window.URL.createObjectURL(new Blob([response.data]));
                              const link = document.createElement('a');
                              link.href = url;
                              link.setAttribute('download', `invoice-${invoice.invoice_number}.pdf`);
                              document.body.appendChild(link);
                              link.click();
                              link.remove();
                            } catch (error) {
                              console.error('Error downloading PDF:', error);
                            }
                          }}
                          className="text-sm text-primary-600 hover:text-primary-700 mt-2"
                        >
                          📄 Download PDF
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Vehicle Detail Modal */}
      {selectedVehicle && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-lg w-full max-w-3xl p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">
                  {selectedVehicle.make} {selectedVehicle.model}
                </h2>
                <p className="text-gray-600">{selectedVehicle.year} • {selectedVehicle.license_plate}</p>
              </div>
              <button
                onClick={() => setSelectedVehicle(null)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="card">
                <h3 className="text-sm font-medium text-gray-500 mb-2">Current Mileage</h3>
                <p className="text-2xl font-bold text-primary-600">
                  {(selectedVehicle.current_mileage || 0).toLocaleString()} km
                </p>
              </div>
              <div className="card">
                <h3 className="text-sm font-medium text-gray-500 mb-2">Service Interval</h3>
                <p className="text-2xl font-bold text-blue-600">
                  {(selectedVehicle.service_interval_km || 10000).toLocaleString()} km
                </p>
              </div>
            </div>

            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Vehicle Details</h3>
              <dl className="space-y-2">
                {selectedVehicle.vin && (
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-500">VIN:</dt>
                    <dd className="text-sm font-medium text-gray-900">{selectedVehicle.vin}</dd>
                  </div>
                )}
                {selectedVehicle.color && (
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-500">Color:</dt>
                    <dd className="text-sm font-medium text-gray-900">{selectedVehicle.color}</dd>
                  </div>
                )}
                <div className="flex justify-between">
                  <dt className="text-sm text-gray-500">Registered:</dt>
                  <dd className="text-sm font-medium text-gray-900">
                    {format(new Date(selectedVehicle.created_at), 'dd.MM.yyyy')}
                  </dd>
                </div>
              </dl>
              {selectedVehicle.notes && (
                <div className="mt-3 p-3 bg-gray-50 rounded-md">
                  <p className="text-sm text-gray-700">{selectedVehicle.notes}</p>
                </div>
              )}
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Service History</h3>
              {workOrders.filter(wo => wo.car_id === selectedVehicle.id).length === 0 ? (
                <p className="text-gray-500 text-center py-4">No service history</p>
              ) : (
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {workOrders
                    .filter(wo => wo.car_id === selectedVehicle.id)
                    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
                    .map((wo) => (
                      <div key={wo.id} className="border-b border-gray-200 last:border-0 pb-3 last:pb-0">
                        <div className="flex justify-between items-start mb-1">
                          <div className="flex items-center gap-2">
                            {getStatusBadge(wo.status)}
                            <span className="text-sm text-gray-600">
                              {format(new Date(wo.created_at), 'dd.MM.yyyy')}
                            </span>
                          </div>
                          {wo.invoice && (
                            <span className="text-sm font-semibold text-green-600">
                              {wo.invoice.total.toFixed(2)} лв
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-700">{wo.reported_issues}</p>
                        {wo.mileage_at_intake && (
                          <p className="text-xs text-gray-500 mt-1">
                            At {wo.mileage_at_intake.toLocaleString()} km
                          </p>
                        )}
                      </div>
                    ))}
                </div>
              )}
            </div>

            <div className="mt-6 pt-4 border-t border-gray-200">
              <button
                onClick={() => setSelectedVehicle(null)}
                className="w-full btn btn-secondary"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

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
