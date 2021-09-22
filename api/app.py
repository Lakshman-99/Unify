import os
import click
from dotenv import load_dotenv
from flask import Flask, request, abort,render_template,send_from_directory,redirect
from flask.cli import AppGroup
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import ChatGrant
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import subprocess
import mysql.connector
mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "root"
    )
mycursor = mydb.cursor()

load_dotenv()
global ls

ls=[]
twilio_client = Client()

app = Flask(__name__)

chatrooms_cli = AppGroup('chatrooms', help='Manage your chat rooms.')
app.cli.add_command(chatrooms_cli)



@chatrooms_cli.command('list', help='list all chat rooms')
def list():
    global ls
    conversations = twilio_client.conversations.conversations.list()
    for conversation in conversations:
        print(f'{conversation.friendly_name}')
        k=conversation.friendly_name
        print(k)
        print(type(k))
        ls.append(k)
        print(ls)

@chatrooms_cli.command('search', help='search all chat rooms')
@click.argument('name')
def search(name):
    global ls
    conversations = twilio_client.conversations.conversations.list()
    for conversation in conversations:
        print(f'{conversation.friendly_name}')
        k=conversation.friendly_name
        ls.append(k)
    print(ls)
    if name in ls:

        print(name)
        return True

    else:
        print("room not found")
        print("available rooms")
        print(ls)
        return ls

@chatrooms_cli.command('create', help='create a chat room')
@click.argument('name')
def create(name):
    conversation = None
    for conv in twilio_client.conversations.conversations.list():
        if conv.friendly_name == name:
            conversation = conv
            break
    if conversation is not None:
        print('Chat room already exists')
    else:
        twilio_client.conversations.conversations.create(friendly_name=name)


@chatrooms_cli.command('delete', help='delete a chat room')
@click.argument('name')
def delete(name):
    conversation = None
    for conv in twilio_client.conversations.conversations.list():
        if conv.friendly_name == name:
            conversation = conv
            break
    if conversation is None:
        print('Chat room not found')
    else:
        conversation.delete()


@app.route('/login', methods=['POST','GET'])
def login():
    global username
    payload = request.get_json(force=True)
    username = payload.get('username')
    if not username:
        abort(401)

    # create the user (if it does not exist yet)
    participant_role_sid = None
    for role in twilio_client.conversations.roles.list():
        if role.friendly_name == 'participant':
            participant_role_sid = role.sid
    try:
        twilio_client.conversations.users.create(identity=username,
                                                 role_sid=participant_role_sid)
    except TwilioRestException as exc:
        if exc.status != 409:
            raise

    # add the user to all the conversations
    conversations = twilio_client.conversations.conversations.list()
    for conversation in conversations:
        try:
            conversation.participants.create(identity=username)
        except TwilioRestException as exc:
            if exc.status != 409:
                raise

    # generate an access token
    twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    twilio_api_key_sid = os.environ.get('TWILIO_API_KEY_SID')
    twilio_api_key_secret = os.environ.get('TWILIO_API_KEY_SECRET')
    service_sid = conversations[0].chat_service_sid
    token = AccessToken(twilio_account_sid, twilio_api_key_sid,
                        twilio_api_key_secret, identity=username)
    token.add_grant(ChatGrant(service_sid=service_sid))

    # send a response
    return {
        'chatrooms': [[conversation.friendly_name, conversation.sid]
                      for conversation in conversations],
        'token': token.to_jwt().decode(),
    }
@app.route('/cr' ,methods=['GET','post'])
def cr():
    return render_template("create.html")
@app.route('/create11' ,methods=['GET','POST'])
def create11():
    return render_template("forms.html")
@app.route('/create1' ,methods=['GET','post'])
def create1():
    name = request.form.get('room')
    print(name)
    subprocess.call([ 'flask' ,'chatrooms' ,'list'])
    global ls
    print(ls)
    conversation = None
    for conv in twilio_client.conversations.conversations.list():
        if conv.friendly_name == name:
            conversation = conv
            break
    if conversation is not None:
        return render_template('forms.html' ,value="oops..group name already exist !")
    else :
        subprocess.call([ 'flask' ,'chatrooms' ,'create' ,name ])
        mycursor.execute("use unify")
        mycursor.execute("insert into log values('%s')"%(name))
        mydb.commit()
        return redirect("http://localhost:3000/")
@app.route('/seapro',methods=['GET','POST'])
def seapro():
    return render_template('form2.html')

@app.route('/search',methods=['GET','POST'])
def search():
    search = request.form.get('search')
    print(search)
    global ls
    conversations = twilio_client.conversations.conversations.list()
    for conversation in conversations:
        print(f'{conversation.friendly_name}')
        k=conversation.friendly_name
        ls.append(k)
    print(ls)
    if search in ls:

        print(search)
        return render_template('form2.html',value3=search,value4="click  -->",value5="<--  to enter")


    else:
        print("room not found")
        print("available rooms")
        print(ls)
        mycursor.execute("use unify")
        mycursor.execute("select * from log")
        l = mycursor.fetchall()
        return render_template('form2.html',value2="oops...no group exist !!")

@app.route('/')
def index():
    return render_template('home.html')
