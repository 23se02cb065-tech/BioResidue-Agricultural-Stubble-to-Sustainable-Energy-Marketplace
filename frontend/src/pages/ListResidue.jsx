import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import api from '../api';
import './ListResidue.css';

// Fix default Leaflet icon
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

function MapPicker({ onSelect }) {
  const [pos, setPos] = useState(null);
  useMapEvents({
    click(e) {
      setPos(e.latlng);
      onSelect(e.latlng);
    },
  });
  return pos ? <Marker position={pos} /> : null;
}

export default function ListResidue() {
  const [form, setForm] = useState({
    crop_type: '', quantity: '', price_per_unit: '',
    description: '', location_name: '', latitude: '', longitude: ''
  });
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleMapSelect = (latlng) => {
    setForm(f => ({ ...f, latitude: latlng.lat.toFixed(6), longitude: latlng.lng.toFixed(6) }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (!form.latitude || !form.longitude) {
      setError('Please click on the map to pin your location');
      return;
    }
    setLoading(true);
    try {
      await api.post('/residues/', form);
      setSuccess('🎉 Residue listed successfully!');
      setForm({ crop_type: '', quantity: '', price_per_unit: '', description: '', location_name: '', latitude: '', longitude: '' });
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to list residue');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="list-page">
      <div className="list-header">
        <h1>🌾 List Crop Residue</h1>
        <p>Add your surplus crop residue to the marketplace</p>
      </div>

      <div className="list-container">
        <form onSubmit={handleSubmit} className="list-form">
          {success && <div className="alert alert-success">{success}</div>}
          {error && <div className="alert alert-error">{error}</div>}

          <div className="form-row">
            <div className="form-group">
              <label>Crop Type</label>
              <input id="crop-type" value={form.crop_type} onChange={e => setForm({ ...form, crop_type: e.target.value })} placeholder="e.g. Wheat Straw, Corn Husks" required />
            </div>
            <div className="form-group">
              <label>Quantity (Metric Tons)</label>
              <input id="quantity" type="number" step="0.1" min="0.1" value={form.quantity} onChange={e => setForm({ ...form, quantity: e.target.value })} placeholder="e.g. 20" required />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Price per Ton (₹)</label>
              <input id="price" type="number" step="0.01" min="0" value={form.price_per_unit} onChange={e => setForm({ ...form, price_per_unit: e.target.value })} placeholder="e.g. 2500" required />
            </div>
            <div className="form-group">
              <label>Location Name</label>
              <input id="location-name" value={form.location_name} onChange={e => setForm({ ...form, location_name: e.target.value })} placeholder="e.g. Amritsar, Punjab" required />
            </div>
          </div>

          <div className="form-group">
            <label>Description (optional)</label>
            <textarea id="description" rows={3} value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} placeholder="Describe the condition, moisture content, baling, etc." />
          </div>

          <div className="form-group">
            <label>📍 Click on the map to pin your location</label>
            {form.latitude && (
              <p className="coords-display">Pinned: {form.latitude}°N, {form.longitude}°E</p>
            )}
            <div className="map-wrapper">
              <MapContainer center={[20.5937, 78.9629]} zoom={5} style={{ height: '320px', borderRadius: '12px' }}>
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                <MapPicker onSelect={handleMapSelect} />
              </MapContainer>
            </div>
          </div>

          <button id="list-submit" type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Listing…' : '🚀 List Residue'}
          </button>
        </form>
      </div>
    </div>
  );
}
