import React, { useState } from 'react';
import api from '../api';
import './Checkout.css';

export default function Checkout({ residue, onClose, onSuccess }) {
  const [step, setStep] = useState(1); // 1=qty, 2=payment
  const [quantity, setQuantity] = useState('');
  const [card, setCard] = useState({ number: '', name: '', expiry: '', cvv: '' });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const totalPrice = quantity ? (parseFloat(quantity) * residue.price_per_unit).toFixed(2) : 0;

  const handleQtyNext = (e) => {
    e.preventDefault();
    const q = parseFloat(quantity);
    if (!q || q <= 0 || q > residue.quantity) {
      setError(`Enter a quantity between 0.1 and ${residue.quantity}`);
      return;
    }
    setError('');
    setStep(2);
  };

  const handlePay = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      // Create order first
      const orderRes = await api.post('/orders/', {
        residue_id: residue.id,
        quantity: parseFloat(quantity)
      });
      const orderId = orderRes.data.order.id;

      // Then pay
      const payRes = await api.post(`/orders/${orderId}/pay`, {
        card_number: card.number
      });

      setResult(payRes.data);
      setStep(3);
    } catch (err) {
      setError(err.response?.data?.error || 'Payment failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="checkout-overlay" onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="checkout-modal">
        <button className="checkout-close" onClick={onClose}>✕</button>

        {step === 1 && (
          <>
            <h2>🛒 Buy Residue</h2>
            <div className="checkout-item-info">
              <strong>{residue.crop_type}</strong>
              <span>📍 {residue.location_name}</span>
              <span>Available: {residue.quantity} tons @ ₹{residue.price_per_unit}/ton</span>
            </div>
            {error && <div className="co-error">{error}</div>}
            <form onSubmit={handleQtyNext}>
              <div className="co-field">
                <label>Quantity (tons)</label>
                <input
                  id="checkout-qty"
                  type="number"
                  min="0.1"
                  max={residue.quantity}
                  step="0.1"
                  value={quantity}
                  onChange={e => setQuantity(e.target.value)}
                  placeholder={`Max ${residue.quantity}`}
                  required
                />
              </div>
              {quantity && <div className="co-total">Total: ₹{parseFloat(totalPrice).toLocaleString()}</div>}
              <button id="checkout-next" type="submit" className="co-btn">Proceed to Payment →</button>
            </form>
          </>
        )}

        {step === 2 && (
          <>
            <h2>💳 Secure Payment</h2>
            <div className="co-summary">
              {residue.crop_type} · {quantity} tons · ₹{parseFloat(totalPrice).toLocaleString()}
            </div>
            <p className="co-hint">💡 Card starting with <code>4000</code> = test failure, any other = success</p>
            {error && <div className="co-error">{error}</div>}
            <form onSubmit={handlePay}>
              <div className="co-field">
                <label>Card Number</label>
                <input id="card-number" value={card.number} onChange={e => setCard({ ...card, number: e.target.value })} placeholder="1234 5678 9012 3456" maxLength={19} required />
              </div>
              <div className="co-field">
                <label>Cardholder Name</label>
                <input id="card-name" value={card.name} onChange={e => setCard({ ...card, name: e.target.value })} placeholder="Name on card" required />
              </div>
              <div className="co-row">
                <div className="co-field">
                  <label>Expiry</label>
                  <input id="card-expiry" value={card.expiry} onChange={e => setCard({ ...card, expiry: e.target.value })} placeholder="MM/YY" maxLength={5} required />
                </div>
                <div className="co-field">
                  <label>CVV</label>
                  <input id="card-cvv" type="password" value={card.cvv} onChange={e => setCard({ ...card, cvv: e.target.value })} placeholder="···" maxLength={4} required />
                </div>
              </div>
              <button id="checkout-pay" type="submit" className="co-btn" disabled={loading}>
                {loading ? 'Processing…' : `Pay ₹${parseFloat(totalPrice).toLocaleString()}`}
              </button>
            </form>
          </>
        )}

        {step === 3 && result && (
          <div className="co-result">
            {result.payment_status === 'success' ? (
              <>
                <div className="co-result-icon success">✅</div>
                <h2>Payment Successful!</h2>
                <p>Ref: <strong>{result.transaction.reference}</strong></p>
                <p>₹{result.transaction.amount.toLocaleString()} paid for {quantity} tons of {residue.crop_type}</p>
                <button className="co-btn" onClick={onSuccess}>Done</button>
              </>
            ) : (
              <>
                <div className="co-result-icon failed">❌</div>
                <h2>Payment Failed</h2>
                <p>The transaction was declined. Please try a different card.</p>
                <button className="co-btn" onClick={() => { setStep(2); setError(''); }}>Try Again</button>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
