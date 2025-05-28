from flask import Blueprint, request, jsonify
from app import db
from app.models import User
from flask_jwt_extended import create_access_token

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'operacional')

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Usuário já existe'}), 400

    user = User(username=username, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Usuário criado com sucesso'}), 201

@bp.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        token = create_access_token(identity={'id': user.id, 'role': user.role})
        return jsonify({'access_token': token}), 200
    return jsonify({'message': 'Credenciais inválidas'}), 401
