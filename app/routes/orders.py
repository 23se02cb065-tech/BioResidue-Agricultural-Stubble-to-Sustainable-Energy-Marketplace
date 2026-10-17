import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.database import db
from app.models import Order, Residue, Transaction

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/', methods=['POST'])
@jwt_required()
def create_order():
    claims = get_jwt()
    if claims.get('role') != 'company':
        return jsonify({'error': 'Only companies can place orders'}), 403

    uid = int(get_jwt_identity())
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    residue_id = data.get('residue_id')
    quantity = float(data.get('quantity', 0))

    if not residue_id or quantity <= 0:
        return jsonify({'error': 'residue_id and positive quantity required'}), 400

    residue = Residue.query.get(residue_id)
    if not residue:
        return jsonify({'error': 'Residue not found'}), 404
    if residue.status != 'available':
        return jsonify({'error': 'Residue is not available'}), 409
    if quantity > residue.quantity:
        return jsonify({'error': f'Only {residue.quantity} tons available'}), 400

    total_price = quantity * residue.price_per_unit
    order = Order(
        residue_id=residue_id,
        company_id=uid,
        quantity=quantity,
        total_price=total_price,
        status='pending'
    )
    db.session.add(order)
    db.session.commit()
    return jsonify({'message': 'Order created', 'order': order.to_dict()}), 201


@orders_bp.route('/<int:order_id>/pay', methods=['POST'])
@jwt_required()
def pay_order(order_id):
    uid = int(get_jwt_identity())
    order = Order.query.get_or_404(order_id)

    if order.company_id != uid:
        return jsonify({'error': 'Unauthorized'}), 403
    if order.status != 'pending':
        return jsonify({'error': 'Order already processed'}), 409

    data = request.get_json() or {}
    card_number = str(data.get('card_number', '')).replace(' ', '')

    # Mock payment logic: card numbers starting with 4000 fail
    if card_number.startswith('4000'):
        tx_status = 'failed'
        order.status = 'cancelled'
    else:
        tx_status = 'success'
        order.status = 'paid'
        # Deduct stock
        residue = Residue.query.get(order.residue_id)
        if residue:
            residue.quantity -= order.quantity
            if residue.quantity <= 0:
                residue.quantity = 0
                residue.status = 'sold'

    tx = Transaction(
        order_id=order.id,
        amount=order.total_price,
        status=tx_status,
        reference=str(uuid.uuid4())[:12].upper()
    )
    db.session.add(tx)
    db.session.commit()

    return jsonify({
        'message': 'Payment processed',
        'payment_status': tx_status,
        'order': order.to_dict(),
        'transaction': tx.to_dict()
    }), 200


@orders_bp.route('/my', methods=['GET'])
@jwt_required()
def my_orders():
    uid = int(get_jwt_identity())
    orders = Order.query.filter_by(company_id=uid).order_by(Order.created_at.desc()).all()
    return jsonify({'orders': [o.to_dict() for o in orders]}), 200
