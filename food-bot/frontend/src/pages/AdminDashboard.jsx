import React, { useState, useEffect } from 'react';
import { adminAPI } from '../api';
import { SalesIcon, OrdersIcon, RatingsIcon, MenuIcon } from '../icons';

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('stalls');
  const [stallsSummary, setStallsSummary] = useState(null);
  const [salesAnalytics, setSalesAnalytics] = useState(null);
  const [flaggedRatings, setFlaggedRatings] = useState(null);
  const [loading, setLoading] = useState(false);

  // Filters for Sales Report
  const [filterStallId, setFilterStallId] = useState('');
  const [filterStartDate, setFilterStartDate] = useState('');
  const [filterEndDate, setFilterEndDate] = useState('');

  // Vendor Creation Form State
  const [vendorForm, setVendorForm] = useState({ name: '', email: '', password: '', stall_id: '' });
  const [vendorMsg, setVendorMsg] = useState({ type: '', text: '' });

  // Fetch Stalls
  const fetchStalls = async () => {
    try {
      const data = await adminAPI.getStallsSummary();
      setStallsSummary(data);
    } catch (err) {
      console.error('Failed to fetch stalls:', err);
    }
  };

  // Fetch Sales
  const fetchSales = async () => {
    try {
      const data = await adminAPI.getSalesAnalytics(filterStallId, filterStartDate, filterEndDate);
      setSalesAnalytics(data);
    } catch (err) {
      console.error('Failed to fetch sales analytics:', err);
    }
  };

  // Fetch Ratings Flags
  const fetchRatings = async () => {
    try {
      const data = await adminAPI.getRatingsAnalytics(3.0);
      setFlaggedRatings(data);
    } catch (err) {
      console.error('Failed to fetch flagged ratings:', err);
    }
  };

  useEffect(() => {
    if (activeTab === 'stalls') fetchStalls();
    if (activeTab === 'sales') fetchSales();
    if (activeTab === 'ratings') fetchRatings();
  }, [activeTab]);

  // Handle Vendor Creation Submit
  const handleVendorSubmit = async (e) => {
    e.preventDefault();
    setVendorMsg({ type: '', text: '' });
    try {
      const payload = {
        name: vendorForm.name,
        email: vendorForm.email,
        password: vendorForm.password,
        stall_id: parseInt(vendorForm.stall_id),
      };
      const res = await adminAPI.createVendor(payload);
      setVendorMsg({ type: 'success', text: `Vendor "${res.name}" (${res.email}) created successfully for ${res.stall_name}!` });
      setVendorForm({ name: '', email: '', password: '', stall_id: '' });
    } catch (err) {
      setVendorMsg({ type: 'error', text: err.message || 'Failed to create vendor.' });
    }
  };

  return (
    <div>
      {/* Top Header Card */}
      <div className="glass-card" style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.5rem' }}>Admin Management & Cross-Stall Analytics</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.2rem' }}>
          Global Campus Food Operations, Sales Audits, and Vendor Provisioning
        </p>
      </div>

      {/* Navigation Tabs */}
      <div className="tab-list">
        <button className={`tab-btn ${activeTab === 'stalls' ? 'active' : ''}`} onClick={() => setActiveTab('stalls')}>
          <OrdersIcon /> All Stalls Overview
        </button>
        <button className={`tab-btn ${activeTab === 'sales' ? 'active' : ''}`} onClick={() => setActiveTab('sales')}>
          <SalesIcon /> Sales Reports
        </button>
        <button className={`tab-btn ${activeTab === 'ratings' ? 'active' : ''}`} onClick={() => setActiveTab('ratings')}>
          <RatingsIcon /> Flagged Ratings (&lt; 3.0)
        </button>
        <button className={`tab-btn ${activeTab === 'vendors' ? 'active' : ''}`} onClick={() => setActiveTab('vendors')}>
          Vendor Provisioning
        </button>
      </div>

      {/* TAB 1: STALLS OVERVIEW */}
      {activeTab === 'stalls' && stallsSummary && (
        <div className="grid-3">
          {stallsSummary.stalls.map((s) => (
            <div key={s.stall_id} className="glass-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                <h3 style={{ fontSize: '1.2rem' }}>{s.stall_name}</h3>
                <span className={`badge ${s.is_open ? 'badge-ready' : 'badge-pending'}`}>
                  {s.is_open ? 'OPEN' : 'CLOSED'}
                </span>
              </div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '1rem' }}><strong>Location:</strong> {s.location}</p>

              <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '0.75rem', fontSize: '0.9rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.25rem 0' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Today's Orders:</span>
                  <strong>{s.today_orders_count}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.25rem 0' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Total Orders:</span>
                  <strong>{s.total_orders_count}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.25rem 0' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Menu Items:</span>
                  <strong>{s.menu_items_count} dishes</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.25rem 0', color: 'var(--success)', fontWeight: 700 }}>
                  <span>Total Revenue:</span>
                  <span>Rs. {s.total_revenue.toFixed(2)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* TAB 2: SALES REPORTS */}
      {activeTab === 'sales' && (
        <div>
          {/* Filters Bar */}
          <div className="glass-card" style={{ marginBottom: '1.5rem' }}>
            <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
              <div style={{ flex: 1, minWidth: '150px' }}>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Filter by Stall ID</label>
                <input
                  type="number"
                  className="form-control"
                  placeholder="e.g. 3"
                  value={filterStallId}
                  onChange={(e) => setFilterStallId(e.target.value)}
                />
              </div>

              <div style={{ flex: 1, minWidth: '150px' }}>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Start Date</label>
                <input
                  type="date"
                  className="form-control"
                  value={filterStartDate}
                  onChange={(e) => setFilterStartDate(e.target.value)}
                />
              </div>

              <div style={{ flex: 1, minWidth: '150px' }}>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>End Date</label>
                <input
                  type="date"
                  className="form-control"
                  value={filterEndDate}
                  onChange={(e) => setFilterEndDate(e.target.value)}
                />
              </div>

              <button className="btn btn-primary" onClick={fetchSales}>
                Apply Filters
              </button>
            </div>
          </div>

          {/* Sales Report Cards */}
          {salesAnalytics && (
            <div>
              <div className="grid-2" style={{ marginBottom: '1.5rem' }}>
                <div className="glass-card">
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Aggregated Revenue</span>
                  <h2 style={{ fontSize: '2.2rem', color: 'var(--success)', marginTop: '0.25rem' }}>
                    Rs. {salesAnalytics.total_revenue.toFixed(2)}
                  </h2>
                </div>
                <div className="glass-card">
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Total Dispatched Items</span>
                  <h2 style={{ fontSize: '2.2rem', color: 'var(--primary)', marginTop: '0.25rem' }}>
                    {salesAnalytics.total_items_sold} items
                  </h2>
                </div>
              </div>

              {/* Stall Breakdown */}
              <div className="glass-card">
                <h3>Revenue & Items Breakdown per Stall</h3>
                <table className="data-table" style={{ marginTop: '1rem' }}>
                  <thead>
                    <tr>
                      <th>Stall Name</th>
                      <th>Items Sold</th>
                      <th>Revenue Generated</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(salesAnalytics.stall_breakdown || {}).map(([sName, sData]) => (
                      <tr key={sName}>
                        <td><strong>{sName}</strong></td>
                        <td>{sData.items_sold} items</td>
                        <td style={{ color: 'var(--success)', fontWeight: 600 }}>Rs. {sData.revenue.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: RATINGS FLAGS */}
      {activeTab === 'ratings' && flaggedRatings && (
        <div className="glass-card">
          <h3>Flagged Low Ratings (Below 3.0 Stars)</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '1.25rem' }}>
            Alerts for food quality or service issues reported by students
          </p>

          <div style={{ marginBottom: '1.5rem' }}>
            <h4>Flagged Order Ratings ({flaggedRatings.total_flagged_order_ratings})</h4>
            {flaggedRatings.flagged_order_ratings.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.5rem' }}>No low order ratings recorded.</p>
            ) : (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Order Code</th>
                    <th>Rating</th>
                    <th>Review Comment</th>
                  </tr>
                </thead>
                <tbody>
                  {flaggedRatings.flagged_order_ratings.map((r) => (
                    <tr key={r.rating_id}>
                      <td><strong>{r.order_code}</strong></td>
                      <td style={{ color: 'var(--accent)', fontWeight: 700 }}><RatingsIcon size={16} /> {r.rating} / 5</td>
                      <td>"{r.review}"</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          <div>
            <h4>Flagged Item Ratings ({flaggedRatings.total_flagged_item_ratings})</h4>
            {flaggedRatings.flagged_item_ratings.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.5rem' }}>No low item ratings recorded.</p>
            ) : (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Stall</th>
                    <th>Dish Name</th>
                    <th>Rating</th>
                    <th>Review</th>
                  </tr>
                </thead>
                <tbody>
                  {flaggedRatings.flagged_item_ratings.map((r) => (
                    <tr key={r.rating_id}>
                      <td>{r.stall_name}</td>
                      <td><strong>{r.item_name}</strong></td>
                      <td style={{ color: 'var(--accent)', fontWeight: 700 }}><RatingsIcon size={16} /> {r.rating} / 5</td>
                      <td>"{r.review}"</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}

      {/* TAB 4: VENDOR MANAGEMENT */}
      {activeTab === 'vendors' && (
        <div className="glass-card" style={{ maxWidth: '540px' }}>
          <h3>Provision New Vendor Account</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '1.25rem' }}>
            Create credentials for a stall manager
          </p>

          {vendorMsg.text && (
            <div
              style={{
                padding: '0.75rem',
                borderRadius: '8px',
                marginBottom: '1rem',
                fontSize: '0.85rem',
                background: vendorMsg.type === 'success' ? 'rgba(16,185,129,0.15)' : 'rgba(244,63,94,0.15)',
                border: `1px solid ${vendorMsg.type === 'success' ? 'var(--success)' : 'var(--accent)'}`,
                color: vendorMsg.type === 'success' ? 'var(--success)' : 'var(--accent)',
              }}
            >
              {vendorMsg.text}
            </div>
          )}

          <form onSubmit={handleVendorSubmit}>
            <div className="form-group">
              <label>Vendor Manager Name</label>
              <input
                type="text"
                className="form-control"
                placeholder="e.g. Diner Manager"
                value={vendorForm.name}
                onChange={(e) => setVendorForm({ ...vendorForm, name: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label>Vendor Email Address</label>
              <input
                type="email"
                className="form-control"
                placeholder="e.g. diner@campus.edu"
                value={vendorForm.email}
                onChange={(e) => setVendorForm({ ...vendorForm, email: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                className="form-control"
                placeholder="Enter account password"
                value={vendorForm.password}
                onChange={(e) => setVendorForm({ ...vendorForm, password: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label>Assigned Stall ID</label>
              <input
                type="number"
                className="form-control"
                placeholder="e.g. 1 (Campus Diner), 2 (Taco), 3 (Basant)"
                value={vendorForm.stall_id}
                onChange={(e) => setVendorForm({ ...vendorForm, stall_id: e.target.value })}
                required
              />
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '0.75rem', marginTop: '0.5rem' }}>
              Provision Vendor Account
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
