from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.database import db
from app.models import Residue, Order, Transaction, Bid

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/', methods=['GET'])
@jwt_required()
def dashboard():
    uid = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get('role')

    if role == 'farmer':
        residues = Residue.query.filter_by(farmer_id=uid).all()
        total_listed = len(residues)
        total_sold = sum(1 for r in residues if r.status == 'sold')
        total_quantity = sum(r.quantity for r in residues)
        residue_ids = [r.id for r in residues]

        paid_orders = Order.query.filter(
            Order.residue_id.in_(residue_ids),
            Order.status == 'paid'
        ).all() if residue_ids else []

        total_revenue = sum(o.total_price for o in paid_orders)

        pending_bids = Bid.query.filter(
            Bid.residue_id.in_(residue_ids),
            Bid.status == 'pending'
        ).all() if residue_ids else []

        return jsonify({
            'role': 'farmer',
            'stats': {
                'total_listed': total_listed,
                'total_sold': total_sold,
                'total_quantity_available': round(total_quantity, 2),
                'total_revenue': round(total_revenue, 2),
                'pending_bids': len(pending_bids)
            },
            'recent_orders': [o.to_dict() for o in paid_orders[-5:]],
            'bids': [b.to_dict() for b in pending_bids]
        }), 200

    elif role == 'company':
        orders = Order.query.filter_by(company_id=uid).order_by(Order.created_at.desc()).all()
        total_spent = sum(o.total_price for o in orders if o.status == 'paid')
        bids = Bid.query.filter_by(company_id=uid).order_by(Bid.created_at.desc()).all()

        return jsonify({
            'role': 'company',
            'stats': {
                'total_orders': len(orders),
                'paid_orders': sum(1 for o in orders if o.status == 'paid'),
                'total_spent': round(total_spent, 2),
                'total_bids': len(bids)
            },
            'recent_orders': [o.to_dict() for o in orders[:10]],
            'bids': [b.to_dict() for b in bids[:10]]
        }), 200

    return jsonify({'error': 'Unknown role'}), 400
