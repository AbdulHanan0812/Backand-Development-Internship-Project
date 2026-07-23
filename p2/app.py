from flask import Flask, request, jsonify
from db import db
from models import User

app = Flask(__name__)
app.secret_key = 'intern_p2'

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///student.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return {"Message" : "Student API IS Working Succesfully!"}



# Create User
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    age = data.get('age')

    if not name or not email or not age:
        return jsonify({"error": "All fields are required!"}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "This email already exists!"}), 409
    
    new_user = User(email=email, name=name, age=age)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully!", "user": new_user.to_dict()}), 201


# All Users Data Read
@app.route("/users", methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200


# Single User Data Read
@app.route("/users/<int:user_id>", methods=['GET'])
def get_single_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


# Update User
@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    user.name = data.get("name", user.name)
    user.age = data.get("age", user.age)

    if "email" in data:
        email_owner = User.query.filter_by(email=data['email']).first()
        if email_owner and email_owner.id != user_id:
            return jsonify({"error": "This email is already used!"}), 409
        user.email = data['email']

    db.session.commit()
    return jsonify({"message": "User updated successfully!", "user": user.to_dict()}), 200


# Delete User
@app.route("/users/<int:user_id>", methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully!"}), 200


if __name__ == "__main__":
    app.run(debug=True)