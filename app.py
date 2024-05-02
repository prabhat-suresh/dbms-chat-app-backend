from flask import Flask, request, jsonify
import psycopg2
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Add this line to enable CORS for all routes

pswd="1234"
port_num="5433"

@app.route('/login', methods=['POST'])
def login():
    # Get username and password from the POST request
    username = request.form.get('username')
    password = request.form.get('password')

    # Connect to the database and validate credentials
    conn = psycopg2.connect(database="discord",
                            user="postgres",
                            password=pswd,
                            host="localhost", port=port_num)

    cur = conn.cursor()

    # Check if the username and password match a record in the database
    cur.execute('''SELECT login('%s','%s');''',
                (username, password))

    user = cur.fetchone()
    isValidLogin=user[0]

    cur.close()
    conn.close()

    if isValidLogin:
        # Successful login, return a success response
        return jsonify({'message': 'Login successful'}), 200
    else:
        # Invalid credentials, return an error response
        return jsonify({'error': 'Invalid username or password'}), 400

@app.route('/servers', methods=['POST'])
def get_user_servers():
    # Get username and password from the POST request
    username = request.form.get('username')
    
    # Connect to the database
    conn = psycopg2.connect(database="discord",
                            user="postgres",
                            password=pswd,
                            host="localhost",
                            port="5433")
    
    cur = conn.cursor()
    
    # Fetch servers where the user is a member
    cur.execute('''SELECT s.name
                   FROM server_member sm
                   INNER JOIN server s ON sm.server_id = s.id
                   WHERE sm.member = %s''', (username,))
    
    servers = cur.fetchall()
    
    cur.close()
    conn.close()

    return jsonify({'servers': [server[0] for server in servers]}), 200

@app.route('/friends/<username>', methods=['POST'])
def get_user_friends(username):
    
    # Connect to the database
    conn = psycopg2.connect(database="discord",
                            user="postgres",
                            password="postgres",
                            host="localhost",
                            port=port_num)
    
    cur = conn.cursor()
    
    # Fetch servers where the user is a member
    cur.execute('''SELECT friends_user(%s)''', (username,))
    
    friends = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # Return the list of servers as JSON response
    return jsonify({'friends': [friend[0] for friend in friends]}), 200


if __name__ == '__main__': 
    app.run(debug=True, port=5000)