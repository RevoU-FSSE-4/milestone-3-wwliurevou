from flask import Blueprint, jsonify, request
from sqlalchemy import and_, null
# from flask_jwt_extended import jwt_required
from connectors.mysql_connector import engine
from models.accounts import Accounts

from sqlalchemy.orm import sessionmaker
from flask_login import current_user, login_required
account_routes = Blueprint("account_routes", __name__)

##
@account_routes.route("/accounts", methods=['GET'])
@login_required
#bisa jwt required
# @jwt_required kalo mau pake ini di postman harus add variable authorization = Bearer token
def get_all_accounts():

    Session = sessionmaker(engine)
    s = Session()
    # with Session() as s:

    try:
        # Logic Apps
        myaccounts=[]
        accounts_query= s.query(Accounts).where(Accounts.user_id == current_user.id)
        results = s.execute(accounts_query)
        for row in results.scalars():
            myaccounts.append({
                'id': row.id,
                'user_id': row.user_id,
                'account_type': row.account_type,
                'account_number': row.account_number,
                'balance': row.balance,
            })
                    # Commit
        return { 'accounts': myaccounts,
            'message':"Hello"+" "+current_user.username+"This is your accounts."}, 200
    
    except Exception as e:
        # Rollback
        print(e)
        # Kirim Error Message
        return { 'message': 'Unexpected Error' }, 500


   


@account_routes.route('/accounts', methods=['POST'])
@login_required

def accounts_insert():
    Session = sessionmaker(engine)
    s = Session()
    s.begin()
    #cuman bisa bikin tiga tipe akun 
    input_account_type = request.form['account_type']

    try:
        if input_account_type not in ['Savings', 'Checking', 'Cash']:
            return { "message": "Invalid account type. Account type should be Savings, Checking, or Cash."  }, 400

        NewAccounts = Accounts(
            account_type=request.form['account_type'],
            account_number=request.form['account_number'],
            balance=request.form['balance'],
            user_id=int(current_user.id), # assuming user_id is linked to current_user.id in your application.
            # Assuming user_id is linked to current_user.id in your application.
        )

        s.add(NewAccounts)
        s.commit()
    except Exception as e:
        print(e)
        s.rollback()
        return { "message": "Failed to create new accounts" }, 500

    return { 'message': 'Successfully created new accounts'}, 200

@account_routes.route("/accounts/<id>", methods=['GET'])
@login_required
#bisa jwt required
# @jwt_required kalo mau pake ini di postman harus add variable authorization = Bearer token
def get_specific_account(id):

    Session = sessionmaker(engine)
    s = Session()
    # with Session() as s:

    try:
        # Logic Apps
        specificAccount=[]
        accounts_query= s.query(Accounts).where(and_(Accounts.id == id,Accounts.user_id == current_user.id))
        results = s.execute(accounts_query)
        for row in results.scalars():
            specificAccount.append({
                'id': row.id,
                'user_id': row.user_id,
                'account_type': row.account_type,
                'account_number': row.account_number,
                'balance': row.balance,
            })
                    # Commit

        ##HARUS IMPLEMENT KALO 
    except Exception as e:
        # Rollback
        print(e)
        # Kirim Error Message
        return { 'message': 'Unexpected Error' }, 500

    return { 'accounts': specificAccount,
            'message':"Hello"+" "+current_user.username+" "+"This is detail of your accounts."}, 200


@account_routes.route('/accounts/<id>', methods=['DELETE'])
@login_required
def accounts_delete(id):
    Session = sessionmaker(engine)
    s = Session()
    s.begin()

    ##check if account is owned by THE USER_ID
    check_account_exist= s.query(Accounts).where(Accounts.user_id == current_user.id, Accounts.id ==id).first()
    if check_account_exist is None:
        return { 'message': 'Account not found' }, 404
    

    try:
        accounts = s.query(Accounts).filter(Accounts.id == id).first()
        s.delete(accounts)
        s.commit()
    except Exception as e:
        print(e)
        s.rollback()
        return { "message": "Fail to Delete" }, 500

    return { 'message': 'Successfully deleted the account'}, 200

@account_routes.route('/accounts/<id>', methods=['PUT'])
@login_required
def accounts_update(id):
    input_account_type= request.form['account_type']
    input_account_number = request.form['account_number']
    input_account_balance=request.form['balance']
    

    # only_account_type = input_account_type != None and input_account_number == None and input_account_balance == None
    # only_account_number = input_account_type == None and input_account_number != None and input_account_balance == None
    # only_account_number = input_account_type == None and input_account_number == None and input_account_balance != None
    # account_type_and_number=
    # account_balance_and_type=
    # account_number_and_balance=
    # account_type_and
    Session = sessionmaker(engine)
    s = Session()
    s.begin()
    before_changes =[]
    after_changes =[]
    try:
        
        check_account= s.query(Accounts).where(Accounts.user_id == current_user.id, Accounts.id ==id).first()
        current_account= s.query(Accounts).filter(Accounts.user_id == current_user.id, Accounts.id ==id)
        get_account_number_query= s.query(Accounts.account_number).where(Accounts.user_id == current_user.id, Accounts.id ==id)
        account_number_from_db = s.execute(get_account_number_query).scalar()
        if check_account is None:
            return { 'message': 'Account not found' }, 404
        ##kalo cmn 1 field berarti itu aja yg di update
        if input_account_type not in ('Savings', 'Checking', 'Cash'):
            return { "message": "Invalid account type. Account type should be Savings, Checking, or Cash."  }, 400
        ##kalo account numbernya sama, kt cmn update the rest of the fields
        ## kalo misalnya smuanya beda, kt update smuanya 
        print("this is number"+account_number_from_db)
        results1 = s.execute(current_account)
        for row in results1.scalars():
            before_changes.append({
                'id': row.id,
                'user_id': row.user_id,
                'account_type': row.account_type,
                'account_number': row.account_number,
                'balance': row.balance,
            })
        if str(account_number_from_db) == str(input_account_number):
            print("account number same")
            check_account.account_type = request.form['account_type']
            check_account.balance = request.form['balance']
            s.commit()
        if str(account_number_from_db) != str(input_account_number):
            check_account.account_type = request.form['account_type']
            check_account.account_number = request.form['account_number']
            check_account.balance = request.form['balance']
            s.commit()
            
        s.commit()
        updated_account = s.query(Accounts).filter(Accounts.user_id == current_user.id, Accounts.id ==id)
        results2 = s.execute(updated_account)
        for row in results2.scalars():
                after_changes.append({
                'id': row.id,
                'user_id': row.user_id,
                'account_type': row.account_type,
                'account_number': row.account_number,
                'balance': row.balance,})
        s.commit()
    except Exception as e:
        print(e)
        s.rollback()
        return { "message": "Failed to Update" }, 500

    return { 'Before Changes' : before_changes,
        'message': 'Successfully updated account data',
        'After changes' : after_changes},200

##bisa ditambain from what to what 
