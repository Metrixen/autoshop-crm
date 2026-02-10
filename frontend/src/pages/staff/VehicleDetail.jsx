import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { format } from 'date-fns';
import StaffLayout from '../../components/StaffLayout';
import { carAPI, workOrderAPI, invoiceAPI } from '../../services/api';

const VehicleDetail = () => {
  const { t } = useTranslation();
  const { id } = useParams();
  const [vehicle, setVehicle] = useState(null);
  const [workOrders, setWorkOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [showMileageModal, setShowMileageModal] = useState(false);
  const [newMileage, setNewMileage] = useState('');
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    loadData();
  }, [id]);

  const loadData = async () => {
    try {
      const [vehicleRes, workOrdersRes] = await Promise.all([
        carAPI.get(id),
        workOrderAPI.list({ car_id: id })
      ]);
      
      setVehicle(vehicleRes.data);
      setWorkOrders(workOrdersRes.data);
    } catch (error) {
      console.error('Error loading vehicle data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateMileage = async () => {
    const mileageValue = parseInt(newMileage);
    
    if (!mileageValue || mileageValue <= 0) {
      alert('Please enter a valid mileage');
      return;
    }
    
    if (mileageValue <= vehicle.current_mileage) {
      alert(`New mileage must be greater than current mileage (${vehicle.current_mileage} km)`);
      return;
    }
    
    try {
      setUpdating(true);
      await carAPI.update(id, { current_mileage: mileageValue });
      await loadData();
      setShowMileageModal(false);
      setNewMileage('');
    } catch (error) {
      console.error('Error updating mileage:', error);
      alert('Failed to update mileage');
    } finally {
      setUpdating(false);
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

  const calculateMileageHistory = () => {
    return workOrders
      .filter(wo => wo.mileage_at_intake)
      .map(wo => ({
        date: new Date(wo.created_at),
        mileage: wo.mileage_at_intake,
        issue: wo.reported_issues
      }))
      .sort((a, b) => a.date - b.date);
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

  if (!vehicle) {
    return (
      <StaffLayout>
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-gray-900">Vehicle not found</h2>
          <Link to="/vehicles" className="text-primary-600 hover:text-primary-700 mt-4 inline-block">
            ← Back to Vehicles
          </Link>
        </div>
      </StaffLayout>
    );
  }

  const mileageHistory = calculateMileageHistory();
  const totalServices = workOrders.filter(wo => wo.status === 'done').length;
  const totalSpent = workOrders
    .filter(wo => wo.invoice)
    .reduce((sum, wo) => sum + (wo.invoice?.total || 0), 0);

  return (
    <StaffLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <Link to="/vehicles" className="text-primary-600 hover:text-primary-700 text-sm mb-2 inline-block">
              ← Back to Vehicles
            </Link>
            <h1 className="text-3xl font-bold text-gray-900">
              {vehicle.make} {vehicle.model}
            </h1>
            <p className="mt-1 text-gray-600">
              {vehicle.year} • {vehicle.license_plate}
            </p>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="card">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-500">
                Current Mileage
              </h3>
              <button
                onClick={() => setShowMileageModal(true)}
                className="text-xs text-primary-600 hover:text-primary-700 font-medium"
              >
                Update
              </button>
            </div>
            <p className="text-3xl font-bold text-primary-600">
              {(vehicle.current_mileage || 0).toLocaleString()}
            </p>
            <p className="text-xs text-gray-500 mt-1">km</p>
          </div>
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Service Interval
            </h3>
            <p className="text-3xl font-bold text-blue-600">
              {(vehicle.service_interval_km || 10000).toLocaleString()}
            </p>
            <p className="text-xs text-gray-500 mt-1">km</p>
          </div>
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Total Services
            </h3>
            <p className="text-3xl font-bold text-green-600">
              {totalServices}
            </p>
          </div>
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Total Spent
            </h3>
            <p className="text-3xl font-bold text-yellow-600">
              {totalSpent.toFixed(2)}
            </p>
            <p className="text-xs text-gray-500 mt-1">лв</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {['overview', 'history', 'mileage'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab
                    ? 'border-primary-600 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab content */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Vehicle Details */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Vehicle Information
              </h3>
              <dl className="space-y-3">
                <div className="flex justify-between">
                  <dt className="text-sm font-medium text-gray-500">Make</dt>
                  <dd className="text-sm text-gray-900">{vehicle.make}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm font-medium text-gray-500">Model</dt>
                  <dd className="text-sm text-gray-900">{vehicle.model}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm font-medium text-gray-500">Year</dt>
                  <dd className="text-sm text-gray-900">{vehicle.year}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm font-medium text-gray-500">License Plate</dt>
                  <dd className="text-sm text-gray-900">{vehicle.license_plate}</dd>
                </div>
                {vehicle.vin && (
                  <div className="flex justify-between">
                    <dt className="text-sm font-medium text-gray-500">VIN</dt>
                    <dd className="text-sm text-gray-900">{vehicle.vin}</dd>
                  </div>
                )}
                {vehicle.color && (
                  <div className="flex justify-between">
                    <dt className="text-sm font-medium text-gray-500">Color</dt>
                    <dd className="text-sm text-gray-900">{vehicle.color}</dd>
                  </div>
                )}
              </dl>
              {vehicle.notes && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <h4 className="text-sm font-medium text-gray-500 mb-2">Notes</h4>
                  <p className="text-sm text-gray-900">{vehicle.notes}</p>
                </div>
              )}
            </div>

            {/* Owner Details */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Owner Information
              </h3>
              <dl className="space-y-3">
                <div className="flex justify-between">
                  <dt className="text-sm font-medium text-gray-500">Name</dt>
                  <dd className="text-sm text-gray-900">
                    {vehicle.owner?.first_name} {vehicle.owner?.last_name}
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm font-medium text-gray-500">Phone</dt>
                  <dd className="text-sm text-gray-900">{vehicle.owner?.phone}</dd>
                </div>
                {vehicle.owner?.email && (
                  <div className="flex justify-between">
                    <dt className="text-sm font-medium text-gray-500">Email</dt>
                    <dd className="text-sm text-gray-900">{vehicle.owner.email}</dd>
                  </div>
                )}
                <div className="flex justify-between">
                  <dt className="text-sm font-medium text-gray-500">Customer Since</dt>
                  <dd className="text-sm text-gray-900">
                    {format(new Date(vehicle.owner?.created_at), 'dd.MM.yyyy')}
                  </dd>
                </div>
              </dl>
              <div className="mt-4 pt-4 border-t border-gray-200">
                <Link
                  to={`/customers/${vehicle.owner_id}`}
                  className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                >
                  View Customer Profile →
                </Link>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Service History ({workOrders.length} visits)
            </h3>
            
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
                        <div className="flex items-center gap-3">
                          <h4 className="font-medium text-gray-900">
                            Work Order #{wo.id}
                          </h4>
                          {getStatusBadge(wo.status)}
                        </div>
                        <p className="text-sm text-gray-600 mt-1">
                          {wo.reported_issues}
                        </p>
                        {wo.diagnostic_notes && (
                          <p className="text-sm text-gray-500 mt-1">
                            <span className="font-medium">Diagnosis:</span> {wo.diagnostic_notes}
                          </p>
                        )}
                      </div>
                      <div className="text-right ml-4">
                        <p className="text-sm text-gray-900">
                          {format(new Date(wo.created_at), 'dd.MM.yyyy')}
                        </p>
                        {wo.mileage_at_intake && (
                          <p className="text-sm text-gray-500">
                            {wo.mileage_at_intake.toLocaleString()} km
                          </p>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm text-gray-500 mt-2">
                      {wo.assigned_mechanic && (
                        <span>
                          👨‍🔧 {wo.assigned_mechanic.first_name} {wo.assigned_mechanic.last_name}
                        </span>
                      )}
                      {wo.invoice && (
                        <span className="font-medium text-green-600">
                          💰 {wo.invoice.total.toFixed(2)} лв
                        </span>
                      )}
                    </div>
                    
                    <div className="flex gap-2 mt-3">
                      <Link
                        to={`/work-orders/${wo.id}`}
                        className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                      >
                        View Work Order →
                      </Link>
                      {wo.invoice && (
                        <Link
                          to={`/invoices/${wo.invoice.id}`}
                          className="text-green-600 hover:text-green-700 text-sm font-medium"
                        >
                          View Invoice →
                        </Link>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'mileage' && (
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Mileage History
            </h3>
            
            {mileageHistory.length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                No mileage data recorded
              </p>
            ) : (
              <div className="space-y-4">
                {mileageHistory.map((entry, index) => {
                  const prevEntry = index > 0 ? mileageHistory[index - 1] : null;
                  const mileageDiff = prevEntry ? entry.mileage - prevEntry.mileage : null;
                  const daysDiff = prevEntry 
                    ? Math.round((entry.date - prevEntry.date) / (1000 * 60 * 60 * 24))
                    : null;
                  const avgPerDay = mileageDiff && daysDiff ? (mileageDiff / daysDiff).toFixed(1) : null;
                  
                  return (
                    <div key={index} className="border-b border-gray-200 last:border-0 pb-4 last:pb-0">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="text-lg font-semibold text-gray-900">
                            {entry.mileage.toLocaleString()} km
                          </p>
                          <p className="text-sm text-gray-600 mt-1">
                            {format(entry.date, 'dd.MM.yyyy')}
                          </p>
                          <p className="text-sm text-gray-500 mt-1">
                            {entry.issue}
                          </p>
                        </div>
                        {mileageDiff && (
                          <div className="text-right">
                            <p className="text-sm font-medium text-primary-600">
                              +{mileageDiff.toLocaleString()} km
                            </p>
                            {daysDiff && (
                              <p className="text-xs text-gray-500">
                                {daysDiff} days ({avgPerDay} km/day)
                              </p>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
            
            {mileageHistory.length > 1 && (
              <div className="mt-6 pt-6 border-t border-gray-200">
                <h4 className="text-sm font-medium text-gray-900 mb-3">Statistics</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Total Distance</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {(mileageHistory[mileageHistory.length - 1].mileage - mileageHistory[0].mileage).toLocaleString()} km
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Average per Service</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {Math.round(
                        (mileageHistory[mileageHistory.length - 1].mileage - mileageHistory[0].mileage) /
                        (mileageHistory.length - 1)
                      ).toLocaleString()} km
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Update Mileage Modal */}
        {showMileageModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Update Vehicle Mileage
              </h3>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Current Mileage: {vehicle.current_mileage.toLocaleString()} km
                </label>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  New Mileage (km)
                </label>
                <input
                  type="number"
                  value={newMileage}
                  onChange={(e) => setNewMileage(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Enter new mileage"
                  autoFocus
                />
                <p className="text-xs text-gray-500 mt-2">
                  New mileage must be greater than {vehicle.current_mileage.toLocaleString()} km
                </p>
              </div>
              <div className="flex gap-2 justify-end">
                <button
                  onClick={() => {
                    setShowMileageModal(false);
                    setNewMileage('');
                  }}
                  className="btn"
                  disabled={updating}
                >
                  Cancel
                </button>
                <button
                  onClick={handleUpdateMileage}
                  className="btn btn-primary"
                  disabled={updating}
                >
                  {updating ? 'Updating...' : 'Update Mileage'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </StaffLayout>
  );
};

export default VehicleDetail;
