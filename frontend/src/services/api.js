import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token expiration
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // Only handle 401 errors on non-auth endpoints
    // Auth endpoints should handle their own errors through normal try/catch
    const isAuthEndpoint = error.config?.url?.startsWith('/api/auth/');
    
    if (error.response?.status === 401 && !isAuthEndpoint) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  customerLogin: (username, password) =>
    api.post('/api/auth/customer/login', { username, password }),
  
  staffLogin: (username, password) =>
    api.post('/api/auth/staff/login', { username, password }),
};

// Customer API
export const customerAPI = {
  list: (params) => api.get('/api/customers', { params }),
  get: (id) => api.get(`/api/customers/${id}`),
  create: (data) => api.post('/api/customers', data),
  update: (id, data) => api.put(`/api/customers/${id}`, data),
  updateMe: (data) => api.put('/api/customers/me', data),
  getMe: () => api.get('/api/customers/me'),
  changePassword: (data) => api.post('/api/customers/me/change-password', data),
};

// Car API
export const carAPI = {
  list: (params) => api.get('/api/cars', { params }),
  get: (id) => api.get(`/api/cars/${id}`),
  getMyCars: () => api.get('/api/cars/my-cars'),
  create: (data) => api.post('/api/cars', data),
  update: (id, data) => api.put(`/api/cars/${id}`, data),
  transferOwnership: (id, data) => api.post(`/api/cars/${id}/transfer-ownership`, data),
  delete: (id) => api.delete(`/api/cars/${id}`),
};

// Work Order API
export const workOrderAPI = {
  list: (params) => api.get('/api/work-orders', { params }),
  get: (id) => api.get(`/api/work-orders/${id}`),
  getMyTasks: (params) => api.get('/api/work-orders/my-tasks', { params }),
  create: (data) => api.post('/api/work-orders', data),
  update: (id, data) => api.put(`/api/work-orders/${id}`, data),
  reassign: (id, data) => api.post(`/api/work-orders/${id}/reassign`, data),
  addLineItem: (id, data) => api.post(`/api/work-orders/${id}/line-items`, data),
  deleteLineItem: (workOrderId, lineItemId) =>
    api.delete(`/api/work-orders/${workOrderId}/line-items/${lineItemId}`),
};

// Invoice API
export const invoiceAPI = {
  list: (params) => api.get('/api/invoices', { params }),
  get: (id) => api.get(`/api/invoices/${id}`),
  createFromWorkOrder: (workOrderId) =>
    api.post(`/api/invoices/from-work-order/${workOrderId}`),
  update: (id, data) => api.put(`/api/invoices/${id}`, data),
  downloadPDF: (id) => api.get(`/api/invoices/${id}/pdf`, { responseType: 'blob' }),
};

// Appointment API
export const appointmentAPI = {
  list: (params) => api.get('/api/appointments', { params }),
  get: (id) => api.get(`/api/appointments/${id}`),
  getPending: () => api.get('/api/appointments/pending'),
  create: (data) => api.post('/api/appointments', data),
  update: (id, data) => api.put(`/api/appointments/${id}`, data),
  convertToWorkOrder: (id) => api.post(`/api/appointments/${id}/convert-to-work-order`),
  delete: (id) => api.delete(`/api/appointments/${id}`),
};

// Staff API
export const staffAPI = {
  list: (params) => api.get('/api/staff', { params }),
  get: (id) => api.get(`/api/staff/${id}`),
  getMechanics: () => api.get('/api/staff/mechanics'),
  create: (data) => api.post('/api/staff', data),
  update: (id, data) => api.put(`/api/staff/${id}`, data),
  delete: (id) => api.delete(`/api/staff/${id}`),
};

// Shop API
export const shopAPI = {
  get: () => api.get('/api/shop'),
  update: (data) => api.put('/api/shop', data),
};

// Reports API
export const reportsAPI = {
  getDashboard: () => api.get('/api/reports/dashboard'),
  getMechanicsPerformance: (params) => api.get('/api/reports/mechanics-performance', { params }),
  getRevenueBreakdown: (params) => api.get('/api/reports/revenue-breakdown', { params }),
  getPopularServices: (params) => api.get('/api/reports/popular-services', { params }),
};

// Admin API
export const adminAPI = {
  listShops: (params) => api.get('/api/admin/shops', { params }),
  getShop: (id) => api.get(`/api/admin/shops/${id}`),
  createShop: (data) => api.post('/api/admin/shops', data),
  toggleFeature: (id, feature, enabled) =>
    api.put(`/api/admin/shops/${id}/toggle-feature`, { feature, enabled }),
  updateSubscription: (id, data) => api.put(`/api/admin/shops/${id}/subscription`, data),
  activateShop: (id) => api.put(`/api/admin/shops/${id}/activate`),
  deactivateShop: (id) => api.put(`/api/admin/shops/${id}/deactivate`),
  getSMSUsage: (id, params) => api.get(`/api/admin/shops/${id}/sms-usage`, { params }),
  impersonate: (id) => api.post(`/api/admin/impersonate/${id}`),
};

export default api;
