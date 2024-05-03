from flask import Flask, request, jsonify
import psycopg2
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Add this line to enable CORS for all routes

# user='Prabhat'
user='Hemanth'

if user=='Prabhat':
    pswd="postgres"
    port_num="5432"
    method='GET'
else:
    pswd="1234"
    port_num="5433"
    method='POST'

@app.route('/login', methods=[method])
def login():
    # Get username and password from the POST request
    username = request.form.get('username')
    password = request.form.get('password')

    # Connect to the database and validate credentials
    conn = psycopg2.connect(database="discord",
                            user="postgres",
                            password=pswd,
                            host="localhost", 
                            port=port_num)

    cur = conn.cursor()

    # Check if the username and password match a record in the database
    cur.execute('''SELECT login(%s,%s);''',
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

@app.route('/servers', methods=[method])
def get_user_servers():
    # Get username and password from the POST request
    username = request.form.get('username')
    
    # Connect to the database
    conn = psycopg2.connect(database="discord",
                            user="postgres",
                            password=pswd,
                            host="localhost",
                            port=port_num)
    
    cur = conn.cursor()
    
    # Fetch servers where the user is a member
    cur.execute('''SELECT servers(%s)''', (username,))
    
    servers = cur.fetchall()
    
    cur.close()
    conn.close()

    def get_values(s):
        i=0
        while True:
            if s[i]==',':
                break
            i=i+1
        return (int(s[1:i]),s[i+2:len(s)-2])

    return jsonify({'servers': [get_values(server[0]) for server in servers]}), 200

@app.route('/friends', methods=[method])
def get_user_friends():
    
    # get username
    username = request.form.get('username')

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


@app.route('/register', methods=[method])
def register():
    # Get email, username and password from the POST request
    email= request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')


    # Connect to the database and validate credentials
    conn = psycopg2.connect(database="discord",
                            user="postgres",
                            password=pswd,
                            host="localhost", 
                            port=port_num)

    cur = conn.cursor()

    # insert new user into relation users
    cur.execute('''insert into users values(%s,%s,%s);''',
                (email, username, password))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Register successful'}), 200



@app.route('/profile',methods=[method])
def profile():
    username= request.form.get('username')
    new_pass= request.form.get('newPassword')

    conn = psycopg2.connect(database="discord",
                            user="postgres",
                            password=pswd,
                            host="localhost", 
                            port=port_num)

    cur = conn.cursor()

    # insert new user into relation users
    cur.execute('''update users set password = %s where user_name = %s''',
                (new_pass,username))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'msg': "succesful"}), 200

@app.route('/email',methods=[method])
def fetchEmail():
    username= request.form.get('username')

    conn = psycopg2.connect(database="discord",
                            user="postgres",
                            password=pswd,
                            host="localhost", 
                            port=port_num)

    cur = conn.cursor()

    #fetch email of username
    cur.execute('''select email from users where user_name = %s''',
                (username,))
    
    email=cur.fetchone()

    cur.close()
    conn.close()

    return jsonify({'email':email[0]}), 200

@app.route('/sendFriendRequest', methods=[method])
def sendFR():
    fromPerson= request.form.get('username')
    toPerson= request.form.get('name')

    conn = psycopg2.connect(database="discord",
                            user="postgres",
                            password=pswd,
                            host="localhost", 
                            port=port_num)

    cur = conn.cursor()

    # insert into friend requests relation
    cur.execute('''insert into friend_request values(%s,%s);''',
                (fromPerson,toPerson))
    
    cur.close()
    conn.close()

    return jsonify({"message":"Request sent"}), 200

@app.route('/sendServerJoinRequest', methods=[method])
def sendSR():
    fromPerson= request.form.get('username')
    toServer= request.form.get('server')

    conn = psycopg2.connect(database="discord",
                            user="postgres",
                            password=pswd,
                            host="localhost", 
                            port=port_num)

    cur = conn.cursor()
    #insert into server join requests 
    cur.execute('''insert into server_join_requests values(%s,%s);''',
                (fromPerson,int(toServer)))
    
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message":"Request sent"}), 200

@app.route('/fetchRequest', methods=[method])
def fetchRequest():
    username= request.form.get('username')

    conn = psycopg2.connect(database="discord",
                            user="postgres",
                            password=pswd,
                            host="localhost", 
                            port=port_num)

    cur = conn.cursor()

    cur.execute('''select sender from friend_request,users where friend_request.receiver = users.user_name and users.user_name = %s;''',
                (username,))
    incomingFriendRequests=cur.fetchall()

    cur.execute('''select friend_req(%s)''',
                (username,))
    outgoingFriendRequests=cur.fetchall()

    cur.execute('''select server_join_requests.server_id, sender from users,server_join_requests,
	roles,server_member_roles,server
	where users.user_name = %s and
	users.user_name = server_member_roles.username
	and server_member_roles.role_id = roles.role_id
	and roles.role_name = 'admin' and roles.server_id = server.id
	and server.id = server_join_requests.server_id;''',
    (username,))
    incomingServerRequests=cur.fetchall()

    cur.execute('''select server_id from users,server_join_requests 
                where users.user_name = server_join_requests.sender
                and users.user_name = %s;''',
                (username,))
    outgoingServerRequests=cur.fetchall()

    cur.close()
    conn.close()

    return jsonify({"incoming":
                    {"friendRequest":[incomingFriendRequest[0] 
                                      for incomingFriendRequest in incomingFriendRequests], 
                                      "serverJoinRequest":[(incomingServerRequest[0],incomingServerRequest[1]) for incomingServerRequest in incomingServerRequests]}, 
                    "outgoing":
                    {"friendRequest":[outgoingFriendRequest[0] 
                                      for outgoingFriendRequest in outgoingFriendRequests], 
                                      "serverJoinRequest":[outgoingServerRequest[0] for outgoingServerRequest in outgoingServerRequests]}}), 200
 

@app.route('/fetchChannels', methods=[method])
def fetchChannels():
    serverID = request.form.get('serverID')

    conn = psycopg2.connect(database="discord",
                            user="postgres",
                            password=pswd,
                            host="localhost", 
                            port=port_num)

    cur = conn.cursor()

    cur.execute('''select id,name from channel where server_id= %s''',
                (serverID,))
    
    channels=cur.fetchall()

    cur.close()
    conn.close()
    return jsonify({"channels":[(channel[0],channel[1]) for channel in channels]}), 200

@app.route('/fetchChannelMessages', methods=[method])
def fetchChannelMessages():
    channelID = request.form.get('channelID')
    conn = psycopg2.connect(database="discord",
                            user="postgres",
                            password=pswd,
                            host="localhost", 
                            port=port_num)

    cur = conn.cursor()

    cur.execute('''select sender,content from channel_message where channel_id=%s order by created_at''',
                (channelID,))
    
    msgs=cur.fetchall()

    cur.close()
    conn.close()
    # I expect messages are sorted according to time stamp
    return jsonify({"messages":[(msg[0],msg[1]) for msg in msgs]}), 200

@app.route('/sendChannelMessage', methods=[method])
def sendChannelMessage():
    sender = request.form.get('username')
    content = request.form.get('content')
    channelID = request.form.get('channelID')

    conn = psycopg2.connect(database="discord",
                            user="postgres",
                            password=pswd,
                            host="localhost", 
                            port=port_num)

    cur = conn.cursor()

    cur.execute(''' insert into channel_message(sender,channel_id,content) values(%s,%s,%s) ''',
                (sender,channelID,content))
    
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message":"Sent successfully"}), 200

@app.route('/fetchDirectMessages/<user1>/<user2>', methods=[method])
def fetchDirectlMessages(user1,user2):
    # user1 = request.form.get('user1')
    # user2 =  request.form.get('user2')
    conn = psycopg2.connect(database="discord",
                            user="postgres",
                            password=pswd,
                            host="localhost", 
                            port=port_num)

    cur = conn.cursor()

    cur.execute('''select sender,content from direct_message
                where sender=%s and receiver=%s or sender=%s and receiver=%s
                order by created_at''',
                (user1,user2,user2,user1))
    
    dms=cur.fetchall()

    cur.close()
    conn.close()
    return jsonify({"messages":[(msg[0],msg[1]) for msg in dms]}), 200


@app.route('/acceptServerJoinRequest', methods=[method])
def acceptServerJoinRequest():
    username= request.form.get('username')
    serverID= request.form.get('serverID')

    conn = psycopg2.connect(database="discord",
                            user="postgres",
                            password=pswd,
                            host="localhost", 
                            port=port_num)

    cur = conn.cursor()


    cur.execute('''insert into server_member values(%s,%s)''',
                (username,serverID))
    cur.execute('''delete from server_join_requests where sender=%s and server_id=%s''',
                (username,serverID))
    

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"messages": "username got added to serverID"}), 200

@app.route('/acceptFriendRequest', methods=[method])
def acceptFriendRequest():
    sender = request.form.get('sender')
    receiver = request.form.get('receiver')

    conn = psycopg2.connect(database="discord",
                            user="postgres",
                            password=pswd,
                            host="localhost", 
                            port=port_num)

    cur = conn.cursor()

    cur.execute('''insert into friends values(%s,%s)''',
                (sender,receiver))
    cur.execute('''delete from friend_request where sender=%s and receiver=%s or sender=%s and receiver=%s''',
                (sender,receiver,receiver,sender))
    
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"messages": "sender & receiver are friends"}), 200

@app.route('/rejectServerJoinRequest', methods=[method])
def rejectServerJoinRequest():
    username= request.form.get('username')
    serverID= request.form.get('serverID')

    conn = psycopg2.connect(database="discord",
                            user="postgres",
                            password=pswd,
                            host="localhost", 
                            port=port_num)

    cur = conn.cursor()

    cur.execute('''delete from server_join_requests where sender=%s and server_id=%s''',
                (username,serverID))
    

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"messages": "---"}), 200

@app.route('/rejectFriendRequest', methods=[method])
def rejectFriendRequest():
    sender = request.form.get('sender')
    receiver = request.form.get('receiver')

    conn = psycopg2.connect(database="discord",
                            user="postgres",
                            password=pswd,
                            host="localhost", 
                            port=port_num)

    cur = conn.cursor()

    cur.execute('''delete from friend_request where sender=%s and receiver=%s or sender=%s and receiver=%s''',
                (sender,receiver,receiver,sender))
    
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"messages": "---"}), 200
   

if __name__ == '__main__': 
    app.run(debug=True, port=5000)