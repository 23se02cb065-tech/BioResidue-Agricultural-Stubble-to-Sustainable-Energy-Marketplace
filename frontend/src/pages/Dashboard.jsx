import React, { useState, useEffect } from 'react';
import api from '../api';
import { useAuth } from '../AuthContext';
import './Dashboard.css';

export default function Dashboard() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/dashboard/').then(res => {
      setData(res.data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="dash-loading">Loading dashboard…</div>;
  if (!data) return <div className="dash-loading">Failed to load dashboard.</div>;

  const { stats, recent_orders, bids } = data;

  return (
    <div className="dash-page">
      <div className="dash-header">
        <h1>📊 Dashboard</h1>
        <p>Welcome back, <strong>{user?.username}</strong> ({user?.role})</p>
      </div>

      <div className="stats-grid">
        {user?.role === 'farmer' ? (
          <>
            <StatCard icon="🌾" label="Listings" value={stats.total_listed} />
            <StatCard icon="✅" label="Sold" value={stats.total_sold} />
            <StatCard icon="📦" label="Tons Available" value={stats.total_quantity_available} />
            <StatCard icon="💰" label="Revenue (₹)" value={`₹${stats.total_revenue?.toLocaleString()}`} />
            <StatCard icon="📋" label="Pending Bids" value={stats.pending_bids} />
          </>
        ) : (
          <>
            <StatCard icon="🛒" label="Total Orders" value={stats.total_orders} />
            <StatCard icon="✅" label="Paid Orders" value={stats.paid_orders} />
            <StatCard icon="💰" label="Total Spent" value={`₹${stats.total_spent?.toLocaleString()}`} />
            <StatCard icon="📋" label="Total Bids" value={stats.total_bids} />
          </>
        )}
      </div>

      {recent_orders?.length > 0 && (
        <section className="dash-section">
          <h2>Recent Orders</h2>
          <div className="order-list">
            {recent_orders.map(o => (
              <div key={o.id} className="order-row">
                <div className="order-info">
                  <strong>{o.crop_type}</strong>
                  <span>{o.location_name}</span>
                </div>
                <div className="order-meta">
                  <span>{o.quantity} tons</span>
                  <span>₹{o.total_price?.toLocaleString()}</span>
                  <span className={`status-badge ${o.status}`}>{o.status}</span>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {bids?.length > 0 && (
        <section className="dash-section">
          <h2>Bids</h2>
          <div className="order-list">
            {bids.map(b => (
              <div key={b.id} className="order-row">
                <div className="order-info">
                  <strong>{b.crop_type}</strong>
                  <span>{b.company_username || b.farmer_username}</span>
                </div>
                <div className="order-meta">
                  <span>₹{b.bid_price_per_unit}/ton</span>
                  <span>{b.quantity} tons</span>
                  <span className={`status-badge ${b.status}`}>{b.status}</span>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

function StatCard({ icon, label, value }) {
  return (
    <div className="stat-card">
      <div className="stat-icon">{icon}</div>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}
