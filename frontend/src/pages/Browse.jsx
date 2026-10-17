import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import api from '../api';
import { useAuth } from '../AuthContext';
import Checkout from '../components/Checkout';
import './Browse.css';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

export default function Browse() {
  const { user } = useAuth();
  const [residues, setResidues] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState('sql');
  const [loading, setLoading] = useState(true);
  const [checkoutItem, setCheckoutItem] = useState(null);

  const fetchResidues = async (q = '') => {
    setLoading(true);
    try {
      const params = q ? { q } : {};
      const res = await api.get('/residues/', { params });
      setResidues(res.data.residues || []);
      setSearchType(res.data.search_type || 'sql');
    } catch {
      setResidues([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchResidues(); }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchResidues(searchQuery.trim());
  };

  const handleCheckoutDone = () => {
    setCheckoutItem(null);
    fetchResidues(searchQuery.trim());
  };

  const validMarkers = residues.filter(r => r.latitude && r.longitude);

  return (
    <div className="browse-page">
      {checkoutItem && (
        <Checkout residue={checkoutItem} onClose={() => setCheckoutItem(null)} onSuccess={handleCheckoutDone} />
      )}

      <div className="browse-header">
        <h1>🗺️ Browse Residues</h1>
        <form onSubmit={handleSearch} className="search-bar">
          <input
            id="search-input"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            placeholder="Search by crop type, description, location…"
          />
          <button id="search-btn" type="submit">Search</button>
        </form>
        {searchType === 'semantic' && (
          <p className="search-badge">🤖 Semantic AI search active</p>
        )}
      </div>

      {/* Map */}
      {validMarkers.length > 0 && (
        <div className="map-section">
          <MapContainer center={[20.5937, 78.9629]} zoom={5} style={{ height: '340px' }}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            {validMarkers.map(r => (
              <Marker key={r.id} position={[r.latitude, r.longitude]}>
                <Popup>
                  <strong>{r.crop_type}</strong><br />
                  {r.location_name}<br />
                  {r.quantity} tons @ ₹{r.price_per_unit}/ton
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>
      )}

      {/* Cards */}
      <div className="cards-section">
        {loading ? (
          <div className="loading-spinner">Loading residues…</div>
        ) : residues.length === 0 ? (
          <div className="empty-state">No residues found. Try a different search.</div>
        ) : (
          <div className="cards-grid">
            {residues.map(r => (
              <div key={r.id} className="residue-card">
                {r.match_score !== undefined && (
                  <div className={`match-badge ${r.match_score >= 70 ? 'high' : r.match_score >= 40 ? 'mid' : 'low'}`}>
                    {r.match_score}% match
                  </div>
                )}
                <div className="card-crop">{r.crop_type}</div>
                <div className="card-farmer">by {r.farmer_username || 'Unknown'}</div>
                <div className="card-details">
                  <span>📦 {r.quantity} tons</span>
                  <span>💰 ₹{r.price_per_unit}/ton</span>
                  <span>📍 {r.location_name}</span>
                </div>
                {r.description && <p className="card-desc">{r.description}</p>}
                <div className="card-total">Total: ₹{(r.quantity * r.price_per_unit).toLocaleString()}</div>
                {user?.role === 'company' && (
                  <button
                    id={`buy-${r.id}`}
                    className="buy-btn"
                    onClick={() => setCheckoutItem(r)}
                  >
                    Buy Residue
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
