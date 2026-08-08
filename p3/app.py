from flask import Flask, jsonify, request
from db import db
from models import User, bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os

app = Flask(__name__)

#home
@app.route('/',methods =['GET'])
def home():
    return jsonify({"MEssage":"Welcome to the Decodelab Internship Project No:3"})


# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key-decodelabs' 

# Extensions Initialize
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

# Database tables 
with app.app_context():
    db.create_all()

# 1. SIGNUP ROUTE 
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json(force=True)
    
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({"error": "All fields are required!"}), 400

    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already registered!"}, 409)

    # Password Hash 
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    new_user = User(name=name, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully!",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email
        }
    }), 201

# 2. LOGIN ROUTE (JWT Token Generation)
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required!"}), 400

    user = User.query.filter_by(email=email).first()

    # Password verify 
    if user and bcrypt.check_password_hash(user.password, password):
        # Generate JWT Token (VIP Wristband)
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            "message": "Login successful!",
            "access_token": access_token
        }), 200

    return jsonify({"error": "Invalid email or password!"}), 401

# 3. PROTECTED ROUTE 
@app.route('/dashboard', methods=['GET'])
@jwt_required()  
def dashboard():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    return jsonify({
        "message": "Welcome to the secure dashboard!",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }), 200

if __name__ == '__main__':
    app.run(debug=True)