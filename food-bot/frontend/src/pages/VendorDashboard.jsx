import React, { useState, useEffect } from 'react';
import { vendorAPI } from '../api';
import { ChefIcon, MenuIcon, OrdersIcon, RatingsIcon, SalesIcon, BellIcon, CheckIcon } from '../icons';

export default function VendorDashboard() {
  const [activeTab, setActiveTab] = useState('orders');
  const [orders, setOrders] = useState([]);
  const [menuItems, setMenuItems] = useState([]);
  const [ratings, setRatings] = useState(null);
  const [sales, setSales] = useState(null);
  const [isOpen, setIsOpen] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Modal State for Menu Item Add/Edit
  const [showItemModal, setShowItemModal] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [itemForm, setItemForm] = useState({ name: '', price: '', half_price: '', available: true });

  // Fetch Live Orders
  const fetchOrders = async () => {
    try {
      const data = await vendorAPI.getOrders();
      setOrders(data.orders || []);
    } catch (err) {
      console.error('Failed to fetch orders:', err);
    }
  };

  // Poll orders every 5 seconds
  useEffect(() => {
    fetchOrders();
    const interval = setInterval(fetchOrders, 5000);
    return () => clearInterval(interval);
  }, []);

  // Fetch Menu Items
  const fetchMenuItems = async () => {
    try {
      const data = await vendorAPI.getMenuItems();
      setMenuItems(data.menu_items || []);
    } catch (err) {
      console.error('Failed to fetch menu:', err);
    }
  };

  // Fetch Ratings
  const fetchRatings = async () => {
    try {
      const data = await vendorAPI.getRatings();
      setRatings(data);
    } catch (err) {
      console.error('Failed to fetch ratings:', err);
    }
  };

  // Fetch Sales
  const fetchSales = async () => {
    try {
      const data = await vendorAPI.getSales();
      setSales(data);
    } catch (err) {
      console.error('Failed to fetch sales:', err);
    }
  };

  useEffect(() => {
    if (activeTab === 'menu') fetchMenuItems();
    if (activeTab === 'ratings') fetchRatings();
    if (activeTab === 'sales') fetchSales();
  }, [activeTab]);

  // Update Order Status
  const handleUpdateOrderStatus = async (orderId, newStatus) => {
    try {
      await vendorAPI.updateOrderStatus(orderId, newStatus);
      fetchOrders();
    } catch (err) {
      alert('Failed to update status: ' + err.message);
    }
  };

  // Toggle Stall Open/Closed
  const handleToggleStall = async (e) => {
    const checked = e.target.checked;
    setIsOpen(checked);
    try {
      await vendorAPI.toggleStallStatus(checked);
    } catch (err) {
      alert('Failed to toggle stall status: ' + err.message);
      setIsOpen(!checked);
    }
  };

  // Handle Add/Edit Menu Item Submit
  const handleItemSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        name: itemForm.name,
        price: parseFloat(itemForm.price),
        half_price: itemForm.half_price ? parseFloat(itemForm.half_price) : null,
        available: itemForm.available,
      };

      if (editingItem) {
        await vendorAPI.updateMenuItem(editingItem.id, payload);
      } else {
        await vendorAPI.createMenuItem(payload);
      }

      setShowItemModal(false);
      fetchMenuItems();
    } catch (err) {
      alert('Failed to save menu item: ' + err.message);
    }
  };

  // Handle Delete Menu Item
  const handleDeleteItem = async (itemId) => {
    if (window.confirm('Are you sure you want to delete this menu item?')) {
      try {
        await vendorAPI.deleteMenuItem(itemId);
        fetchMenuItems();
      } catch (err) {
        alert('Failed to delete item: ' + err.message);
      }
    }
  };

  const openAddModal = () => {
    setEditingItem(null);
    setItemForm({ name: '', price: '', half_price: '', available: true });
    setShowItemModal(true);
  };

  const openEditModal = (item) => {
    setEditingItem(item);
    setItemForm({
      name: item.name,
      price: item.price,
      half_price: item.half_price || '',
      available: item.available,
    });
    setShowItemModal(true);
  };

  return (
    <div>
      {/* Top Header Card */}
      <div className="glass-card" style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.6rem' }}><ChefIcon />Vendor Control Center</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.2rem' }}>
            Live Order Queue & Menu Operations (Real-time sync with WhatsApp Bot)
          </p>
        </div>

        {/* Stall Toggle */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', background: 'rgba(255,255,255,0.9)', padding: '0.45rem 0.9rem', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
          <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>
            Stall Status: <strong style={{ color: isOpen ? 'var(--success)' : 'var(--accent)' }}>{isOpen ? 'OPEN' : 'CLOSED'}</strong>
          </span>
          <label className="switch">
            <input type="checkbox" checked={isOpen} onChange={handleToggleStall} />
            <span className="slider"></span>
          </label>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="tab-list">
        <button className={`tab-btn ${activeTab === 'orders' ? 'active' : ''}`} onClick={() => setActiveTab('orders')}>
          <OrdersIcon /> Live Orders ({orders.length})
        </button>
        <button className={`tab-btn ${activeTab === 'menu' ? 'active' : ''}`} onClick={() => setActiveTab('menu')}>
          <MenuIcon /> Menu Management
        </button>
        <button className={`tab-btn ${activeTab === 'ratings' ? 'active' : ''}`} onClick={() => setActiveTab('ratings')}>
          <RatingsIcon /> Customer Ratings
        </button>
        <button className={`tab-btn ${activeTab === 'sales' ? 'active' : ''}`} onClick={() => setActiveTab('sales')}>
          <SalesIcon /> Sales & Revenue
        </button>
      </div>

      {/* TAB 1: LIVE ORDERS */}
      {activeTab === 'orders' && (
        <div>
              {orders.length === 0 ? (
            <div className="glass-card" style={{ textAlign: 'center', padding: '3rem' }}>
              <div style={{ fontSize: '2.5rem' }}><BellIcon /></div>
              <h3 style={{ marginTop: '1rem' }}>No Live Orders in Queue</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
                New student pre-orders placed via WhatsApp will appear here instantly.
              </p>
            </div>
          ) : (
            <div className="grid-2">
              {orders.map((ord) => (
                <div key={ord.order_id} className="glass-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <span style={{ fontFamily: 'var(--font-heading)', fontSize: '1.2rem', fontWeight: 700, color: 'var(--primary)' }}>
                      {ord.order_code || `ORD-#${ord.order_id}`}
                    </span>
                    <span className={`badge badge-${ord.status.toLowerCase()}`}>{ord.status}</span>
                  </div>

                  <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                    Pickup Time: <strong style={{ color: 'white' }}>{ord.pickup_time || 'Immediate'}</strong> | Student Reg: {ord.student_id}
                  </div>

                  <div style={{ borderTop: '1px solid var(--border-color)', borderBottom: '1px solid var(--border-color)', padding: '0.75rem 0', margin: '0.75rem 0' }}>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.4rem', textTransform: 'uppercase' }}>Items Ordered:</div>
                    {ord.items.map((item, idx) => (
                      <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', padding: '0.2rem 0' }}>
                        <span>• {item.item_name} ({item.portion}) x{item.quantity}</span>
                        <span>Rs. {(item.price * item.quantity).toFixed(2)}</span>
                      </div>
                    ))}
                  </div>

                  {/* Status Action Buttons */}
                  <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
                    {ord.status === 'CONFIRMED' && (
                      <button className="btn btn-primary" style={{ flex: 1, display: 'flex', gap: '0.5rem', alignItems: 'center', justifyContent: 'center' }} onClick={() => handleUpdateOrderStatus(ord.order_id, 'PREPARING')}>
                        <ChefIcon /> Mark Preparing
                      </button>
                    )}
                    {ord.status === 'PREPARING' && (
                      <button className="btn btn-success" style={{ flex: 1, display: 'flex', gap: '0.5rem', alignItems: 'center', justifyContent: 'center' }} onClick={() => handleUpdateOrderStatus(ord.order_id, 'READY')}>
                        <CheckIcon /> Mark Ready for Pickup
                      </button>
                    )}
                    {ord.status === 'READY' && (
                      <button className="btn btn-success" style={{ flex: 1, display: 'flex', gap: '0.5rem', alignItems: 'center', justifyContent: 'center' }} onClick={() => handleUpdateOrderStatus(ord.order_id, 'COMPLETED')}>
                        <RatingsIcon /> Complete & Request Rating
                      </button>
                    )}
                    {ord.status !== 'COMPLETED' && ord.status !== 'CANCELLED' && (
                      <button className="btn btn-outline" style={{ color: 'var(--accent)' }} onClick={() => handleUpdateOrderStatus(ord.order_id, 'CANCELLED')}>
                        Cancel
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: MENU MANAGEMENT */}
      {activeTab === 'menu' && (
        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <h3>Menu Items ({menuItems.length})</h3>
            <button className="btn btn-primary" onClick={openAddModal}>+ Add New Dish</button>
          </div>

          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Dish Name</th>
                <th>Full Price</th>
                <th>Half Price</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {menuItems.map((item) => (
                <tr key={item.id}>
                  <td>#{item.id}</td>
                  <td><strong>{item.name}</strong></td>
                  <td>Rs. {item.price.toFixed(2)}</td>
                  <td>{item.half_price ? `Rs. ${item.half_price.toFixed(2)}` : <span style={{ color: 'var(--text-muted)' }}>N/A</span>}</td>
                  <td>
                    <span className={`badge ${item.available ? 'badge-ready' : 'badge-pending'}`}>
                      {item.available ? 'Available' : 'Out of Stock'}
                    </span>
                  </td>
                  <td>
                    <button className="btn btn-outline" style={{ padding: '0.3rem 0.6rem', marginRight: '0.5rem' }} onClick={() => openEditModal(item)}>
                      Edit
                    </button>
                    <button className="btn btn-danger" style={{ padding: '0.3rem 0.6rem' }} onClick={() => handleDeleteItem(item.id)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* TAB 3: RATINGS */}
      {activeTab === 'ratings' && (
        <div className="glass-card">
          <div style={{ display: 'flex', gap: '2rem', alignItems: 'center', marginBottom: '1.5rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border-color)' }}>
              <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <RatingsIcon size={28} />
                <span style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--warning)' }}>{ratings ? ratings.average_rating : '0.0'}</span>
              </div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Average Rating ({ratings ? ratings.total_reviews : 0} reviews)</p>
            </div>
          </div>

          {ratings && ratings.ratings && ratings.ratings.length > 0 ? (
            <div>
              {ratings.ratings.map((r, idx) => (
                <div key={idx} style={{ padding: '0.75rem 0', borderBottom: '1px solid var(--border-color)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><RatingsIcon size={16} /><strong>{r.rating} / 5</strong> — Student: {r.student_id}</div>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{new Date(r.created_at).toLocaleDateString()}</span>
                  </div>
                  {r.review && <p style={{ marginTop: '0.3rem', fontStyle: 'italic', color: 'var(--text-muted)' }}>"{r.review}"</p>}
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: 'var(--text-muted)' }}>No customer ratings recorded yet.</p>
          )}
        </div>
      )}

      {/* TAB 4: SALES */}
      {activeTab === 'sales' && sales && (
        <div>
          <div className="grid-3" style={{ marginBottom: '1.5rem' }}>
            <div className="glass-card">
              <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Total Revenue</span>
              <h2 style={{ fontSize: '2rem', color: 'var(--success)', marginTop: '0.25rem' }}>Rs. {sales.total_revenue.toFixed(2)}</h2>
            </div>
            <div className="glass-card">
              <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Total Items Sold</span>
              <h2 style={{ fontSize: '2rem', color: 'var(--primary)', marginTop: '0.25rem' }}>{sales.total_items_sold}</h2>
            </div>
          </div>

          <div className="glass-card">
            <h3>Item Sales Breakdown</h3>
            <table className="data-table" style={{ marginTop: '1rem' }}>
              <thead>
                <tr>
                  <th>Dish Name</th>
                  <th>Quantity Sold</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(sales.item_breakdown || {}).map(([name, qty]) => (
                  <tr key={name}>
                    <td><strong>{name}</strong></td>
                    <td>{qty} items</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* MODAL FOR ADD/EDIT MENU ITEM */}
      {showItemModal && (
        <div className="modal-overlay">
          <div className="glass-card modal-content">
            <h3>{editingItem ? 'Edit Menu Item' : 'Add New Dish'}</h3>
            <form onSubmit={handleItemSubmit} style={{ marginTop: '1rem' }}>
              <div className="form-group">
                <label>Dish Name</label>
                <input
                  type="text"
                  className="form-control"
                  value={itemForm.name}
                  onChange={(e) => setItemForm({ ...itemForm, name: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Full Price (Rs.)</label>
                <input
                  type="number"
                  step="0.01"
                  className="form-control"
                  value={itemForm.price}
                  onChange={(e) => setItemForm({ ...itemForm, price: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Half Price (Rs., optional)</label>
                <input
                  type="number"
                  step="0.01"
                  className="form-control"
                  value={itemForm.half_price}
                  onChange={(e) => setItemForm({ ...itemForm, half_price: e.target.value })}
                />
              </div>

              <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <input
                  type="checkbox"
                  id="available"
                  checked={itemForm.available}
                  onChange={(e) => setItemForm({ ...itemForm, available: e.target.checked })}
                />
                <label htmlFor="available" style={{ margin: 0 }}>Available for Order</label>
              </div>

              <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1.5rem' }}>
                <button type="button" className="btn btn-outline" style={{ flex: 1 }} onClick={() => setShowItemModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>
                  Save Dish
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
