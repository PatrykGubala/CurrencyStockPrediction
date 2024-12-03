from flask import Blueprint, request, jsonify, session
from ..models.database import db
from ..models.models import User
from sqlalchemy.exc import IntegrityError
import firebase_admin
from firebase_admin import auth
from firebase_admin.auth import InvalidIdTokenError, ExpiredIdTokenError

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    firebase_uid = data.get('firebase_uid')
    email = data.get('email', '').lower().strip()
    username = data.get('username', '').strip()
    if not firebase_uid or not email or not username:
        return jsonify({'error': 'Firebase UID, email, and username are required'}), 400
    existing_user = User.query.filter_by(firebase_uid=firebase_uid).first()
    if existing_user:
        return jsonify({'message': 'User already exists in the database'}), 200
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already in use'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already in use'}), 400
    new_user = User(firebase_uid=firebase_uid, email=email, username=username)
    db.session.add(new_user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        try:
            auth.delete_user(firebase_uid)
        except firebase_admin.auth.UserNotFoundError:
            pass
        return jsonify({'error': 'Failed to register user in database. User deleted from Firebase.'}), 500
    return jsonify({'message': 'User registered successfully in database'}), 201

@user_bp.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    id_token = data.get('id_token')
    if not id_token:
        return jsonify({'error': 'ID token is required'}), 400
    try:
        decoded_token = auth.verify_id_token(id_token)
        firebase_uid = decoded_token['uid']
    except (InvalidIdTokenError, ExpiredIdTokenError):
        return jsonify({'error': 'Invalid or expired ID token'}), 401
    user = User.query.filter_by(firebase_uid=firebase_uid).first()
    if not user:
        email = decoded_token.get('email', '')
        username = decoded_token.get('name', '')
        user = User(firebase_uid=firebase_uid, email=email, username=username)
        db.session.add(user)
        db.session.commit()
    session['user_id'] = user.id
    return jsonify({'message': 'Logged in successfully'}), 200

@user_bp.route('/logout', methods=['POST'])
def logout_user():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'}), 200

@user_bp.route('/protected', methods=['GET'])
def protected_route():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'message': f'Hello user {user_id}! This is a protected route.'}), 200
