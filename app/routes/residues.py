from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.database import db
from app.models import Residue, User

try:
    from chroma_client import chroma_client
    CHROMA_AVAILABLE = True
except Exception:
    CHROMA_AVAILABLE = False

residues_bp = Blueprint('residues', __name__)


@residues_bp.route('/', methods=['GET'])
def get_residues():
    """Get all available residues (public)."""
    search_query = request.args.get('q', '').strip()
    
    if search_query and CHROMA_AVAILABLE:
        # Try semantic search first
        results = chroma_client.search_residues(search_query, limit=50)
        if results is not None:
            ids = [r['id'] for r in results]
            if not ids:
                return jsonify({'residues': [], 'search_type': 'semantic'}), 200
            residues = Residue.query.filter(
                Residue.id.in_(ids),
                Residue.status == 'available'
            ).all()
            # Order by semantic rank and add match score
            id_to_residue = {r.id: r for r in residues}
            ordered = []
            for r in results:
                res = id_to_residue.get(r['id'])
                if res:
                    d = res.to_dict()
                    d['match_score'] = round((1 - r['distance']) * 100, 1)
                    ordered.append(d)
            return jsonify({'residues': ordered, 'search_type': 'semantic'}), 200

    # SQL fallback (text search or all)
    query = Residue.query.filter_by(status='available')
    if search_query:
        like = f'%{search_query}%'
        query = query.filter(
            (Residue.crop_type.ilike(like)) |
            (Residue.description.ilike(like)) |
            (Residue.location_name.ilike(like))
        )
    residues = query.order_by(Residue.created_at.desc()).all()
    data = []
    for r in residues:
        d = r.to_dict()
        d['match_score'] = 100.0  # SQL results always show as 100%
        data.append(d)
    return jsonify({'residues': data, 'search_type': 'sql'}), 200


@residues_bp.route('/', methods=['POST'])
@jwt_required()
def create_residue():
    claims = get_jwt()
    if claims.get('role') != 'farmer':
        return jsonify({'error': 'Only farmers can list residues'}), 403

    uid = int(get_jwt_identity())
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required = ['crop_type', 'quantity', 'price_per_unit', 'location_name', 'latitude', 'longitude']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400

    residue = Residue(
        farmer_id=uid,
        crop_type=data['crop_type'],
        quantity=float(data['quantity']),
        price_per_unit=float(data['price_per_unit']),
        description=data.get('description', ''),
        location_name=data['location_name'],
        latitude=float(data['latitude']),
        longitude=float(data['longitude']),
        status='available'
    )
    db.session.add(residue)
    db.session.commit()

    # Index in ChromaDB if available
    if CHROMA_AVAILABLE:
        chroma_client.index_residue(residue)

    return jsonify({'message': 'Residue listed successfully', 'residue': residue.to_dict()}), 201


@residues_bp.route('/my', methods=['GET'])
@jwt_required()
def my_residues():
    claims = get_jwt()
    if claims.get('role') != 'farmer':
        return jsonify({'error': 'Only farmers can view their residues'}), 403
    uid = int(get_jwt_identity())
    residues = Residue.query.filter_by(farmer_id=uid).order_by(Residue.created_at.desc()).all()
    return jsonify({'residues': [r.to_dict() for r in residues]}), 200


@residues_bp.route('/<int:residue_id>', methods=['GET'])
def get_residue(residue_id):
    residue = Residue.query.get_or_404(residue_id)
    return jsonify(residue.to_dict()), 200


@residues_bp.route('/<int:residue_id>', methods=['DELETE'])
@jwt_required()
def delete_residue(residue_id):
    uid = int(get_jwt_identity())
    residue = Residue.query.get_or_404(residue_id)
    if residue.farmer_id != uid:
        return jsonify({'error': 'Unauthorized'}), 403
    if CHROMA_AVAILABLE:
        chroma_client.remove_residue(residue_id)
    db.session.delete(residue)
    db.session.commit()
    return jsonify({'message': 'Deleted'}), 200
