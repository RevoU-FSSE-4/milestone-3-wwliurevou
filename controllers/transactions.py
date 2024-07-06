from flask import Blueprint, jsonify, request
# from flask_jwt_extended import jwt_required
from connectors.mysql_connector import engine
from models.accounts import Accounts
from models.transactions import Transactions
from sqlalchemy import and_, select, union_all,exc
from sqlalchemy.orm import sessionmaker
from flask_login import current_user, login_required

transaction_routes = Blueprint("transaction_routes", __name__)


@transaction_routes.route("/transactions", methods=['GET'])
@login_required
#bisa jwt required
# @jwt_required kalo mau pake ini di postman harus add variable authorization = Bearer token
def transaction_list():
    Session = sessionmaker(engine)
    s = Session()
    # with Session() as s:
    user=current_user.id
    try:
        # Logic Apps
        transactions_query_1= s.query(Transactions).join(Accounts,Transactions.from_account_id==Accounts.id).where(Accounts.user_id == user)
        transactions_query_2= s.query(Transactions).join(Accounts,Transactions.to_account_id == Accounts.id).where(Accounts.user_id == user)
        transactions_query=union_all(transactions_query_1, transactions_query_2)
        print("This is the account"+str(transactions_query))
        # print(account_query)
        # transaction_query = s.query(Transactions).where(or_(Transactions.from_account_id in (account_query), Transactions.to_account_id in (account_query)))
        # transaction_query = s.query(Transactions).distinct(Transactions.id).join(Accounts, onclause=Accounts.id == Transactions.to_account_id).filter((Accounts.id ==Transactions.from_account_id)| (Accounts.id==Transactions.to_account_id)).order_by(Accounts.id, Transactions.to_account_id)
        
        ##ini query yang bener 
        # transaction_query = s.query(Transactions).distinct(Transactions.id).join(Accounts,Accounts.id == Transactions.to_account_id)

        ##the logic is to 1. only show account number that belongs to current user id
        ## 2. only how transactions that have account number in to or from 
        transaction_final= select(Transactions).from_statement(transactions_query)
        results = s.execute(transaction_final)
        print(str(results))
        # search_keyword = request.args.get('query')
        # if search_keyword != None:
        #     product_query = product_query.where(Product.name.like(f"%{search_keyword}%"))
        transaction=[]
        for row in results.scalars():
            transaction.append({
                'id': int(row.id),
                'from_account_id': row.from_account_id,
                'to_account_id': row.to_account_id,
                'amount': row.amount,
                'type': row.type,
                'description': row.description,
                'created_At': row.created_at,
            })
                    # Commit
          
    except Exception as e:
        # Rollback
        print(e)
        # Kirim Error Message
        return { 'message': 'Unexpected Error' }, 500
    return { 'Transactions': transaction,
            'message':"Please see your transactions" }, 200

   


@transaction_routes.route('/transactions', methods=['POST'])
@login_required

def transaction_insert():
    Session = sessionmaker(engine)
    s = Session()
    s.begin()
    check_account_id_from = request.form['from_account_id']
    check_account_id_to = request.form['to_account_id']
    input_type = request.form['type']
    input_amount = request.form['amount']
    get_balance_query =s.query(Accounts.balance).where(Accounts.user_id==current_user.id,Accounts.id ==check_account_id_from)
    get_account_to_type_query =s.query(Accounts.account_type).where(Accounts.user_id==current_user.id,Accounts.user_id==current_user.id,Accounts.id ==check_account_id_to)
    get_account_from_type_query =s.query(Accounts.account_type).where(Accounts.user_id==current_user.id,Accounts.user_id==current_user.id,Accounts.id ==check_account_id_from)
    account_type_to = s.execute(get_account_to_type_query).scalar()
    account_type_from = s.execute(get_account_from_type_query).scalar()
    account_balance = s.execute(get_balance_query).scalar()
    try:
    ## make sure account number itu punya dia
        get_accounts_query= s.query(Accounts).where(Accounts.user_id == current_user.id, Accounts.id ==check_account_id_from).first()
        if get_accounts_query is None:
            return { "message": "Account number does not exist" }, 500
        ## make sure kalo type of transactionnya cmn deposit, transfer dan withdrawal
        elif input_type not in('deposit','transfer','withdrawal'):
            return { "message": "Invalid transaction type, you can only enter : deposit, transfer, withdrawal" }, 500
        elif check_account_id_to == check_account_id_from:
            return { "message": "Cannot transfer to the same account" }, 500
    ## update balance of transactionny
    ##gaboleh account number yang sama 
    ##check kalo balance tuh ada jg bisa
    ##kalo transfer berati yg to + ,yang from - 
    ##additional - gabisa transfer dri cash
        elif request.form['type'] == 'transfer':
            account_balance = s.execute(get_balance_query).scalar()
            print("This is account balance"+str(account_balance))
            if int(account_balance) < int(input_amount) :
                return { "message": "Insufficient balance, you only have" +" "+str(account_balance)+" "+"left in your account"  }, 500
            
            else:
                update_balance_query = s.query(Accounts).filter(Accounts.id == check_account_id_from).update({Accounts.balance: Accounts.balance - input_amount})
                s.commit()
                update_balance_query = s.query(Accounts).filter(Accounts.id == check_account_id_to).update({Accounts.balance: Accounts.balance + input_amount})
                s.commit()
        elif request.form['type'] == 'deposit':
            ##need to create cash account
            if int(account_balance) < int(input_amount): 
                return { "message": "Insufficient balance, you only have" +" "+str(account_balance)+" "+"left in your account"  }, 500
            elif account_type_from != 'Cash':
                return { "message": "Invalid account type, you can only deposit from cash account" }, 500
            else:
                update_balance_query = s.query(Accounts).filter(Accounts.id == check_account_id_from).update({Accounts.balance: Accounts.balance + input_amount})
                s.commit()
        elif request.form['type'] == 'withdrawal':

            if int(account_balance) < int(input_amount):
                return { "message": "Insufficient balance, you only have" +" "+str(account_balance)+" "+"left in your account"  }, 500
            elif  account_type_to != 'Cash':
                return { "message": "Invalid account type, you can only withdraw to cash account" }, 500
            else:
                update_balance_query = s.query(Accounts).filter(Accounts.id == check_account_id_from).update({Accounts.balance: Accounts.balance - input_amount})
                s.commit()
##bisa bikin harus ada akun cash withdrawal
            NewTransaction =  Transactions(
            from_account_id=request.form['from_account_id'],
            to_account_id=request.form['to_account_id'],
            amount = request.form['amount'],
            type = request.form['type'],
            description = request.form['description'],
            )
            s.add(NewTransaction)
            s.commit()
    except Exception as e:
        print(e)
        s.rollback()
        return { "message": "Fail to ad" }, 500

    return { 'message': 'You have succesfully '+ str(input_type)+' the amount of '+str(input_amount)+' to the account '+str(check_account_id_to) }, 200

@transaction_routes.route('/transactionswithaccountnumber', methods=['POST'])
@login_required

def new_transaction():
    Session = sessionmaker(engine)
    s = Session()
    # with Session() as s:
    user=current_user.id
    check_account_number_from = request.form['from_account_number']
    check_account_number_to = request.form['to_account_number']

    try:
    ## make sure account number itu punya dia
        get_accounts_query= s.query(Accounts).where(Accounts.user_id == current_user.id, Accounts.id ==check_account_number_from)
        if get_accounts_query == None:
            raise ValueError('Account number does not exist')
    except (ValueError, IndexError):
        return { "message": "Account Number not found" }, 404
    pass
    

    ## make sure account number itu punya dia
    check_from_query= s.query(Transactions).join(Accounts,Transactions.from_account_id==Accounts.id).where(Accounts.user_id == user)

    ## make sure kalo type of transactionnya cmn deposit, transfer dan withdrawal
    ## account number cmn boleh yang ada di database doang. 
    ## update balance of transactionny
    ##gaboleh account number yang sama 



@transaction_routes.route("/transactions/<id>", methods=['GET'])
@login_required
#bisa jwt required
# @jwt_required kalo mau pake ini di postman harus add variable authorization = Bearer token
def get_specific_account(id):

    Session = sessionmaker(engine)
    s = Session()
    # with Session() as s:

    try:
        # Logic Apps
        specificTransaction=[]
        ## transactions and accounts, we need accounts.user id == current user id , transactions id needs to belong to account id 
        transactions_quer_by_id= s.query(Transactions).join(Accounts,Transactions.from_account_id==Accounts.id).where(Accounts.user_id == current_user.id).filter(Transactions.id ==id)
        print(str(transactions_quer_by_id))
        results = s.execute(transactions_quer_by_id)
        for row in results.scalars():
            specificTransaction.append({
                'id': int(row.id),
                'from_account_id': row.from_account_id,
                'to_account_id': row.to_account_id,
                'amount': row.amount,
                'type': row.type,
                'description': row.description,
                'created_At': row.created_at,
            })
                    # Commit

        ##HARUS IMPLEMENT KALO 
    except Exception as e:
        # Rollback
        print(e)
        # Kirim Error Message
        return { 'message': 'Unexpected Error' }, 500

    return { 'Transactions': specificTransaction,
            'message':"Hello"+" "+"This is detail of the specific Transactions."}, 200
