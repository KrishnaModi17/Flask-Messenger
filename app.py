from flask import Flask,render_template,request,redirect,url_for,session,jsonify
from flask_socketio import SocketIO,join_room,leave_room
from flask_cors import CORS,cross_origin
from flask_pymongo import PyMongo
import logging

logging.basicConfig(filename="log.log",format='%(asctime)s :: %(levelname)s :: %(message)s',filemode="w")
logger=logging.getLogger(__name__)

app=Flask(__name__)
socketio=SocketIO(app)

app.secret_key='BAD_SECRET_KEY'

CORS_ORIGINS = ['http://127.0.0.1:5000']
CORS(app, origins=CORS_ORIGINS)

app.config["MONGO_URI"] = "mongodb://localhost:27017/ChatDB"
db = PyMongo(app).db

user_data={}
friend_req=[]

@app.route('/') 
@app.route('/home')
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/register',methods=['GET','POST'])
def register():
    return render_template('register.html')

@app.route('/register_check',methods=['GET','POST'])
def register_check():
    global user_data
    if(request.method=='POST'):
        req=request.form
        req=dict(req)
        session['uid'] = req['uid']
        session['password'] = req['password']
        query=db.users.find({'uid':req['uid']})
        flag=0
        for x in query:
            if(x['uid']==req['uid']):
                flag=1
                break
        reg_dict={
            "uid":req['uid'],
            "email":req['email'],
            "password":req['password'],
            "friends":[]
        }
        req_from={
            'uid':req['uid'],
            'req':[]
        }
        if(flag==0):
            db.users.insert_one(reg_dict)
            db.req_from.insert_one(req_from)
            uid=req['uid']
            user_data[uid]={}
            user_data[uid]['cid']=None
            user_data[uid]['user_list']=[]
            user_data[uid]['friend_list']=[]
            user_data[uid]['group_list']=[]
            user_data[uid]['msg_list']={}
            return redirect('/chat/'+str(uid))
        else:
            return render_template('invalid.html',message="User already registered!!")
    return render_template('register.html')

@app.route('/login_check',methods=['GET','POST']) 
def login_check():
    global user_data
    if(request.method=='POST'):
        req=request.form
        session['uid'] = req['uid']
        session['password'] = req['password']
        req=dict(req)
        query=db.users.find({'uid':req['uid']})
        flag=0
        temp=None
        for x in query:
            if(x['uid']==req['uid']):
                flag=1
                temp=x
                break
        if(flag==1):
            if(temp['password']==req['password']):
                uid=req['uid']
                user_data[uid]={}
                user_data[uid]['cid']=None
                user_data[uid]['user_list']=[]
                user_data[uid]['friend_list']=[]
                user_data[uid]['group_list']=[]
                user_data[uid]['msg_list']={}
                return redirect('/chat/'+str(uid))
            else:
                logger.warn('Incorrect password.Username:{} and Password:{}'.format(temp['password'],
                                                                                       temp['uid']))
                return render_template('invalid.html',message='Incorrect Password!!')
        else:
            logger.warn('Unregistered User')
            return render_template('invalid.html',message='User is not registered!!')
    return render_template('login.html')

@app.route('/Friends/<string:user_id>',methods=['GET','POST'])
def Friends(user_id):
    global user_data
    data=db.users.find_one({ "uid":user_id,"friends": { "$exists": True } })
    user_data[user_id]['friend_list']=data['friends']
    return redirect('/chat/'+str(user_id))
        
@app.route('/Groups/<string:user_id>',methods=['GET','POST'])
def Groups(user_id):
    global user_data
    try:
        file1=open("Groups.txt",'r')
        data=file1.readlines()
        user_data[user_id]['group_list']=data 
        return redirect('/chat/'+str(user_id))
    except:
        return render_template('invalid.html',message='No File found')

@app.route('/update_cid/<string:user_id>/<string:chat_id>',methods=['GET','POST'])
def update_cid(user_id,chat_id):
    global user_data
    user_data[user_id]['cid']=chat_id
    return redirect('/chat/'+str(user_id))

@app.route('/logout',methods=['GET','POST'])
def logout():
    if 'uid' in session:  
        session.clear()
    return redirect(url_for('login'))

@app.route('/chat/<string:user_id>',methods=['GET','POST'])
def chat(user_id):
     global user_data
     
     if(user_id in user_data):
        return render_template('chat.html',uid=user_id,
                                            cid=user_data[user_id]['cid'],
                                            requests=user_data[user_id]['user_list'],
                                            friends=user_data[user_id]['friend_list'],
                                            groups=user_data[user_id]['group_list'],
                                            msg_list=user_data[user_id]['msg_list'])
     
     return redirect('/login')

@app.route('/friend_check',methods=['GET','POST'])
def friend_check():
    if(request.method=='POST'):
        req=request.form['uid']
        query=db.users.find_one({'uid':req})
        flag=0
        if query:
            flag=1
        if(flag==1):
            t=db.req_from.update_one({'uid':req},
                                    {
                                        '$push':{'req':session['uid']}
                                    })
            logger.info('request sent')
            logger.info('{} has got friend request'.format(req))
            return redirect('/chat/'+str(session['uid']))
        else:
            logger.warn('Unregistered User')
            return render_template('invalid.html',message='User not Registered!!')
    return render_template('chat.html')

# @app.route('/friend_request/<req>')
# def friend_request(req):
#     global user_data
#     document =db.req_from.find_one({"uid": req})
#     frnd=document['req']
#     # print(document['friend_request_from'])
#     file1 = open('friend_req.txt','w')
#     file1.truncate()
#     with open('friend_req.txt','w') as file1:
#         for value in frnd:
#             # print(value)
#             file1.write(value)
#             file1.write("/n")
#     file1.close()
#     return redirect(url_for('chat',ugser_id=session['uid']))

@app.route('/access_request/<string:user_id>',methods=['GET','POST'])
def access_request(user_id):
    global user_data
    data=db.req_from.find_one({ "uid":user_id,"req": { "$exists": True } })
    if data:
        user_data[user_id]['user_list']=data['req']
        return redirect('/chat/'+str(user_id))
    else:
        return render_template('invalid.html',message='No friend request')
    
@app.route('/add_friend',methods=['GET','POST'])
def add_friend():
    frnd = request.form["frnd"]
    uid=session['uid']
    db.req_from.update_one({"uid" : uid}, {"$pull" : {'req':frnd}})
    db.users.update_one({'uid':uid},
                        {
                            '$push':{'friends':frnd}
                        })
    return redirect('/chat/'+str(uid))

@app.route('/remove_req',methods=['GET','POST'])
def remove_req():
    frnd = request.form["frnd"]
    uid=session['uid']
    db.req_from.update_one({"uid" : uid}, {"$pull" : {'req':frnd}})
    return redirect('/chat/'+str(uid))

# @app.route('/update_friend_req/<string:user_id>/<string:friend>')
# def update_friend_req(user_id,friend):
#     query = {"uid": user_id}
#     update = {"$pull": {"friend_request_from": {"uid": friend}}}
#     db.users.update_one(query,update)
#     return redirect(url_for('friend_request',req=user_id))

@socketio.on('send_message')
def handle_send_message_event(data):
    logger.info("{} has sent message {}".format(data['uid'],data['message']))
    socketio.emit('receive_message', data)

@socketio.on('join_room')
def handle_chat_event(data):
    logger.warn("{} has joined the room".format(data['username']))
    join_room(data['username'])
    socketio.emit('join_room_announcement', data)

@socketio.on('leave_room')
def handle_room_leave_event(data):
    logger.warn("{} has left the room".format(data['username']))
    leave_room(data['room'])
    socketio.emit('leave_room_announcement', data)

@app.route('/print_message',methods=['POST'])
def print_message():
    data=request.get_json()
    print(f"Received message from {data['uid']}:{data['message']}")
    return jsonify({'status':'OK'})

if __name__=='__main__':
    socketio.run(app,debug=True)
