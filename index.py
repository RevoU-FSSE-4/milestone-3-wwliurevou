from datetime import datetime, timedelta
import os
from flask import Flask, Response, request, session
from dotenv import load_dotenv
from connectors.mysql_connector import connection
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text,select
from controllers.users import user_routes
from controllers.transactions import transaction_routes
from controllers.accounts import account_routes

from flask_login import LoginManager, current_user
# from flask_jwt_extended import JWTManager
from models.accounts import Accounts
from models.users import Users
load_dotenv()
from flask import Flask, Response, redirect, url_for, request, session, abort, g

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.register_blueprint(transaction_routes)
app.register_blueprint(user_routes)
app.register_blueprint(account_routes)
# jwt=JWTManager(app) ##jason web token

##biar bisa login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    Session = sessionmaker(connection)
    s = Session()
    return s.query(Users).get(int(user_id))


@app.route("/")
def hello_world():
        
    # Session = sessionmaker(connection)
    # s = Session()
    # s.permanent = True
    # app.permanent_session_lifetime = timedelta(second=10)
    # print("user timedout")

    #mau insert data to product table 
    
    # Session = sessionmaker(connection)
    # #start transaction

    # with Session() as s:
    #     s.execute(text("INSERT INTO product(name,price,description) VALUES('TAS',10000,'KULITSAPI')"))
    #     s.commit()
        #harus bikin kalo input nya valid baru commit, kalo ga valid berarti execute

      
        #insert data pake sqlalchemy

        # newProduct = Product(name="123",price=1000,description="dari batu")
        # Session = sessionmaker(connection)
        # with Session() as s:
        #         s.add(newProduct)
        #         s.commit()

        #select data, buat select kt harus import select dar sqlalchemy
        account_query = select(Accounts)
        Session = sessionmaker(connection)
        with Session() as s:
            accounts = s.execute(account_query)
            for row in accounts.scalars():
                print(f'ID: {row.id}, Name: {row.username}')
        return "Product inserted!"


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=300)
    session.modified = True
    g.user = current_user