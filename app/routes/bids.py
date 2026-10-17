from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.database import db
from app.models import Bid, Residue

bids_bp = Blueprint('bids', __name__)


@bids_bp.route('/', methods=['POST'])
@jwt_required()
def place_bid():
    claims = get_jwt()
    if claims.get('role') != 'company':
        return jsonify({'error': 'Only companies can place bids'}), 403

    uid = int(get_jwt_identity())
    data = request.get_json() or {}

    residue_id = data.get('residue_id')
    bid_price = float(data.get('bid_price_per_unit', 0))
    quantity = float(data.get('quantity', 0))

    if not residue_id or bid_price <= 0 or quantity <= 0:
        return jsonify({'error': 'residue_id, bid_price_per_unit, and quantity are required'}), 400

    residue = Residue.query.get(residue_id)
    if not residue or residue.status != 'available':
        return jsonify({'error': 'Residue not available'}), 404

    bid = Bid(residue_id=residue_id, company_id=uid, bid_price_per_unit=bid_price, quantity=quantity)
    db.session.add(bid)
    db.session.commit()
    return jsonify({'message': 'Bid placed', 'bid': bid.to_dict()}), 201


@bids_bp.route('/residue/<int:residue_id>', methods=['GET'])
@jwt_required()
def bids_for_residue(residue_id):
    uid = int(get_jwt_identity())
    residue = Residue.query.get_or_404(residue_id)
    if residue.farmer_id != uid:
        return jsonify({'error': 'Unauthorized'}), 403
    bids = Bid.query.filter_by(residue_id=residue_id).order_by(Bid.bid_price_per_unit.desc()).all()
    return jsonify({'bids': [b.to_dict() for b in bids]}), 200


@bids_bp.route('/<int:bid_id>/respond', methods=['POST'])
@jwt_required()
def respond_bid(bid_id):
    uid = int(get_jwt_identity())
    bid = Bid.query.get_or_404(bid_id)
    residue = Residue.query.get(bid.residue_id)
    if not residue or residue.farmer_id != uid:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json() or {}
    action = data.get('action')
    if action not in ['accept', 'reject']:
        return jsonify({'error': 'action must be accept or reject'}), 400

    bid.status = 'accepted' if action == 'accept' else 'rejected'
    db.session.commit()
    return jsonify({'message': f'Bid {bid.status}', 'bid': bid.to_dict()}), 200
