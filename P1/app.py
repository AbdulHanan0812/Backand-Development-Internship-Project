from flask import Flask , jsonify , request

app = Flask(__name__)
app.secret_key = "intern"

users = []

@app.route("/" , methods = ["GET"])
def get_user():
    return jsonify({"users": users}),200


@app.route("/" , methods = ["POST"])
def add_user():
    new_user = request.get_json()
    
    if not new_user:
        return jsonify({"Invalid Credentials, Try Again"}),400
    
    users.append(new_user)  
    
     
   
    return jsonify ({
       
        
        "users" :new_user,
        
        "Message ":" User Created Successfully ",
       
          }),201
    
if __name__ == "__main__":
    app.run(debug=True)
        
   

