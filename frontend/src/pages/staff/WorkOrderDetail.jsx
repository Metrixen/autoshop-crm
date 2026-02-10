import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { format } from 'date-fns';
import StaffLayout from '../../components/StaffLayout';
import { workOrderAPI } from '../../services/api';

const WorkOrderDetail = () => {
  const { t } = useTranslation();
  const { id } = useParams();
  const navigate = useNavigate();
  const [workOrder, setWorkOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({
    status: '',
    diagnostic_notes: '',
    mechanic_notes: '',
    mileage_at_intake: ''
  });

  useEffect(() => {
    loadWorkOrder();
  }, [id]);

  const loadWorkOrder = async () => {
    try {
      const response = await workOrderAPI.get(id);
      setWorkOrder(response.data);
      setFormData({
        status: response.data.status,
        diagnostic_notes: response.data.diagnostic_notes || '',
        mechanic_notes: response.data.mechanic_notes || '',
        mileage_at_intake: response.data.mileage_at_intake || ''
      });
    } catch (error) {
      console.error('Error loading work order:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (newStatus) => {
    if (updating) return;
    
    try {
      setUpdating(true);
      await workOrderAPI.update(id, { status: newStatus });
      await loadWorkOrder();
    } catch (error) {
      console.error('Error updating status:', error);
      alert('Failed to update status');
    } finally {
      setUpdating(false);
    }
  };

  const handleSaveChanges = async () => {
    if (updating) return;
    
    try {
      setUpdating(true);
      const updateData = {};
      
      if (formData.diagnostic_notes !== (workOrder.diagnostic_notes || '')) {
        updateData.diagnostic_notes = formData.diagnostic_notes;
      }
      if (formData.mechanic_notes !== (workOrder.mechanic_notes || '')) {
        updateData.mechanic_notes = formData.mechanic_notes;
      }
      if (formData.mileage_at_intake && formData.mileage_at_intake !== workOrder.mileage_at_intake) {
        updateData.mileage_at_intake = parseInt(formData.mileage_at_intake);
      }
      
      if (Object.keys(updateData).length > 0) {
        await workOrderAPI.update(id, updateData);
        await loadWorkOrder();
        setEditMode(false);
      }
    } catch (error) {
      console.error('Error saving changes:', error);
      alert('Failed to save changes');
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

  const getNextStatus = (currentStatus) => {
    const statusFlow = {
      created: 'diagnosing',
      diagnosing: 'in_progress',
      in_progress: 'done',
      done: null
    };
    return statusFlow[currentStatus];
  };

  const getPrevStatus = (currentStatus) => {
    const statusFlow = {
      diagnosing: 'created',
      in_progress: 'diagnosing',
      done: 'in_progress',
      created: null
    };
    return statusFlow[currentStatus];
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

  if (!workOrder) {
    return (
      <StaffLayout>
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-gray-900">Work order not found</h2>
          <Link to="/work-orders" className="text-primary-600 hover:text-primary-700 mt-4 inline-block">
            ← Back to Work Orders
          </Link>
        </div>
      </StaffLayout>
    );
  }

  const nextStatus = getNextStatus(workOrder.status);
  const prevStatus = getPrevStatus(workOrder.status);

  return (
    <StaffLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <Link to="/work-orders" className="text-primary-600 hover:text-primary-700 text-sm mb-2 inline-block">
              ← Back to Work Orders
            </Link>
            <h1 className="text-3xl font-bold text-gray-900">
              Work Order #{workOrder.id}
            </h1>
            <p className="mt-1 text-gray-600">
              Created {format(new Date(workOrder.created_at), 'dd.MM.yyyy')}
            </p>
          </div>
          <div className="flex items-center gap-3">
            {getStatusBadge(workOrder.status)}
          </div>
        </div>

        {/* Status Control */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Status Management
          </h3>
          <div className="flex items-center gap-3">
            {prevStatus && (
              <button
                onClick={() => handleStatusChange(prevStatus)}
                disabled={updating}
                className="btn"
              >
                ← {prevStatus.replace('_', ' ').toUpperCase()}
              </button>
            )}
            {nextStatus && (
              <button
                onClick={() => handleStatusChange(nextStatus)}
                disabled={updating}
                className="btn btn-primary"
              >
                {nextStatus.replace('_', ' ').toUpperCase()} →
              </button>
            )}
            {workOrder.status === 'done' && (
              <span className="text-green-600 font-medium">✓ Work order completed</span>
            )}
          </div>
          
          {/* Timestamp info */}
          <div className="mt-4 pt-4 border-t border-gray-200 text-sm text-gray-600 space-y-1">
            {workOrder.started_at && (
              <p>Started: {format(new Date(workOrder.started_at), 'dd.MM.yyyy HH:mm')}</p>
            )}
            {workOrder.completed_at && (
              <p>Completed: {format(new Date(workOrder.completed_at), 'dd.MM.yyyy HH:mm')}</p>
            )}
          </div>
        </div>

        {/* Work Order Details */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Customer & Vehicle Info */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Customer & Vehicle
            </h3>
            <dl className="space-y-3">
              <div>
                <dt className="text-sm font-medium text-gray-500">Customer</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {workOrder.customer?.first_name} {workOrder.customer?.last_name}
                  <div className="text-gray-500">{workOrder.customer?.phone}</div>
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Vehicle</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {workOrder.car?.make} {workOrder.car?.model} ({workOrder.car?.year})
                  <div className="text-gray-500">{workOrder.car?.license_plate}</div>
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Assigned Mechanic</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {workOrder.assigned_mechanic ? (
                    `${workOrder.assigned_mechanic.first_name} ${workOrder.assigned_mechanic.last_name}`
                  ) : (
                    <span className="text-gray-400 italic">Unassigned</span>
                  )}
                </dd>
              </div>
            </dl>
          </div>

          {/* Reported Issues */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Reported Issues
            </h3>
            <p className="text-sm text-gray-700 whitespace-pre-wrap">
              {workOrder.reported_issues}
            </p>
          </div>
        </div>

        {/* Notes and Mileage */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Work Details
            </h3>
            {!editMode ? (
              <button
                onClick={() => setEditMode(true)}
                className="btn"
              >
                Edit
              </button>
            ) : (
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    setEditMode(false);
                    setFormData({
                      status: workOrder.status,
                      diagnostic_notes: workOrder.diagnostic_notes || '',
                      mechanic_notes: workOrder.mechanic_notes || '',
                      mileage_at_intake: workOrder.mileage_at_intake || ''
                    });
                  }}
                  className="btn"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveChanges}
                  disabled={updating}
                  className="btn btn-primary"
                >
                  Save Changes
                </button>
              </div>
            )}
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Mileage at Intake (km)
              </label>
              {editMode ? (
                <input
                  type="number"
                  value={formData.mileage_at_intake}
                  onChange={(e) => setFormData({ ...formData, mileage_at_intake: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Enter mileage"
                />
              ) : (
                <p className="text-sm text-gray-900">
                  {workOrder.mileage_at_intake ? (
                    `${workOrder.mileage_at_intake.toLocaleString()} km`
                  ) : (
                    <span className="text-gray-400 italic">Not recorded</span>
                  )}
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Diagnostic Notes
              </label>
              {editMode ? (
                <textarea
                  value={formData.diagnostic_notes}
                  onChange={(e) => setFormData({ ...formData, diagnostic_notes: e.target.value })}
                  rows="4"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Enter diagnostic findings..."
                />
              ) : (
                <p className="text-sm text-gray-900 whitespace-pre-wrap">
                  {workOrder.diagnostic_notes || (
                    <span className="text-gray-400 italic">No diagnostic notes</span>
                  )}
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Mechanic Notes
              </label>
              {editMode ? (
                <textarea
                  value={formData.mechanic_notes}
                  onChange={(e) => setFormData({ ...formData, mechanic_notes: e.target.value })}
                  rows="4"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Enter work performed..."
                />
              ) : (
                <p className="text-sm text-gray-900 whitespace-pre-wrap">
                  {workOrder.mechanic_notes || (
                    <span className="text-gray-400 italic">No mechanic notes</span>
                  )}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Line Items */}
        {workOrder.line_items && workOrder.line_items.length > 0 && (
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Parts & Labor
            </h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Quantity</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Unit Price</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Total</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {workOrder.line_items.map((item) => (
                    <tr key={item.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {item.item_type}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        {item.description}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">
                        {item.quantity}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">
                        {item.unit_price.toFixed(2)} лв
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 text-right">
                        {item.total_price.toFixed(2)} лв
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </StaffLayout>
  );
};

export default WorkOrderDetail;
