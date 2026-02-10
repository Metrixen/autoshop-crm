import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { format } from 'date-fns';
import StaffLayout from '../../components/StaffLayout';
import { invoiceAPI } from '../../services/api';

const Invoices = () => {
  const { t } = useTranslation();
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    loadInvoices();
  }, []);

  const loadInvoices = async () => {
    try {
      const response = await invoiceAPI.list();
      setInvoices(response.data);
    } catch (error) {
      console.error('Error loading invoices:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusClasses = {
      draft: 'badge-info',
      finalized: 'badge-warning',
      paid: 'badge-success',
    };
    
    return (
      <span className={`badge ${statusClasses[status] || 'badge-info'}`}>
        {status.toUpperCase()}
      </span>
    );
  };

  const filteredInvoices = statusFilter === 'all'
    ? invoices
    : invoices.filter(inv => inv.status === statusFilter);

  const statusCounts = {
    all: invoices.length,
    draft: invoices.filter(inv => inv.status === 'draft').length,
    finalized: invoices.filter(inv => inv.status === 'finalized').length,
    paid: invoices.filter(inv => inv.status === 'paid').length,
  };

  const totalRevenue = invoices
    .filter(inv => inv.status === 'paid')
    .reduce((sum, inv) => sum + inv.total, 0);

  const pendingRevenue = invoices
    .filter(inv => inv.status === 'finalized')
    .reduce((sum, inv) => sum + inv.total, 0);

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
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Invoices</h1>
          <p className="mt-2 text-gray-600">
            Manage and track all invoices
          </p>
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
                {status === 'all' ? 'All' : status.toUpperCase()} ({count})
              </button>
            ))}
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Total Invoices
            </h3>
            <p className="text-3xl font-bold text-primary-600">
              {invoices.length}
            </p>
          </div>
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Total Revenue
            </h3>
            <p className="text-3xl font-bold text-green-600">
              {totalRevenue.toFixed(2)}
            </p>
            <p className="text-xs text-gray-500 mt-1">лв</p>
          </div>
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Pending Payment
            </h3>
            <p className="text-3xl font-bold text-yellow-600">
              {pendingRevenue.toFixed(2)}
            </p>
            <p className="text-xs text-gray-500 mt-1">лв</p>
          </div>
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Paid Invoices
            </h3>
            <p className="text-3xl font-bold text-blue-600">
              {statusCounts.paid}
            </p>
          </div>
        </div>

        {/* Invoices table */}
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Invoice #
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Customer
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Vehicle
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredInvoices.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="px-6 py-8 text-center text-gray-500">
                      No invoices found
                    </td>
                  </tr>
                ) : (
                  filteredInvoices.map((invoice) => (
                    <tr key={invoice.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm font-medium text-gray-900">
                          {invoice.invoice_number}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-8 w-8 bg-primary-100 rounded-full flex items-center justify-center">
                            <span className="text-primary-700 text-xs font-semibold">
                              {invoice.customer?.first_name?.[0]}{invoice.customer?.last_name?.[0]}
                            </span>
                          </div>
                          <div className="ml-3">
                            <div className="text-sm font-medium text-gray-900">
                              {invoice.customer?.first_name} {invoice.customer?.last_name}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {invoice.work_order?.car?.make} {invoice.work_order?.car?.model}
                        </div>
                        <div className="text-sm text-gray-500">
                          {invoice.work_order?.car?.license_plate}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-semibold text-gray-900">
                          {invoice.total.toFixed(2)} лв
                        </div>
                        {invoice.tax_amount > 0 && (
                          <div className="text-xs text-gray-500">
                            Tax: {invoice.tax_amount.toFixed(2)} лв
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(invoice.status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {format(new Date(invoice.created_at), 'dd.MM.yyyy')}
                        </div>
                        {invoice.paid_at && (
                          <div className="text-xs text-gray-500">
                            Paid: {format(new Date(invoice.paid_at), 'dd.MM.yyyy')}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <Link
                          to={`/invoices/${invoice.id}`}
                          className="text-primary-600 hover:text-primary-900 mr-3"
                        >
                          View
                        </Link>
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
                          className="text-green-600 hover:text-green-900"
                        >
                          PDF
                        </button>
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

export default Invoices;
