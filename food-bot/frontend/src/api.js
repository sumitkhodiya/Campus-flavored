const BASE_URL = '';

export async function apiRequest(endpoint, method = 'GET', body = null) {
  const token = localStorage.getItem('token');
  
  const headers = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    method,
    headers,
  };

  if (body) {
    config.body = JSON.stringify(body);
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, config);

  if (response.status === 401) {
    localStorage.removeItem('token');
    localStorage.removeItem('user_data');
    window.location.reload();
    throw new Error('Unauthorized');
  }

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'API Request failed');
  }
  return data;
}

export const authAPI = {
  login: (email, password) => apiRequest('/auth/login', 'POST', { email, password }),
};

export const vendorAPI = {
  getOrders: () => apiRequest('/vendor/orders', 'GET'),
  updateOrderStatus: (orderId, status) => apiRequest(`/vendor/orders/${orderId}/status`, 'PATCH', { status }),
  getMenuItems: () => apiRequest('/vendor/menu-items', 'GET'),
  createMenuItem: (itemData) => apiRequest('/vendor/menu-items', 'POST', itemData),
  updateMenuItem: (itemId, itemData) => apiRequest(`/vendor/menu-items/${itemId}`, 'PATCH', itemData),
  deleteMenuItem: (itemId) => apiRequest(`/vendor/menu-items/${itemId}`, 'DELETE'),
  toggleStallStatus: (isOpen) => apiRequest('/vendor/stall/status', 'PATCH', { is_open: isOpen }),
  getRatings: () => apiRequest('/vendor/ratings', 'GET'),
  getSales: () => apiRequest('/vendor/sales', 'GET'),
};

export const adminAPI = {
  getStallsSummary: () => apiRequest('/admin/stalls', 'GET'),
  getSalesAnalytics: (stallId = '', startDate = '', endDate = '') => {
    let query = [];
    if (stallId) query.push(`stall_id=${stallId}`);
    if (startDate) query.push(`start_date=${startDate}`);
    if (endDate) query.push(`end_date=${endDate}`);
    const qStr = query.length ? `?${query.join('&')}` : '';
    return apiRequest(`/admin/sales${qStr}`, 'GET');
  },
  getRatingsAnalytics: (threshold = 3.0) => apiRequest(`/admin/ratings?threshold=${threshold}`, 'GET'),
  createVendor: (vendorData) => apiRequest('/admin/vendors', 'POST', vendorData),
};
