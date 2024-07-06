##buat kasih feature multi role 

from functools import wraps
from flask import jsonify
from flask_login import current_user

def role_required(role):
    #harus bkin dia decorator
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            #authentication logic
            if current_user.is_authenticated and role == 'Admin' and current_user.role == 'Admin':
                return func(*args, **kwargs)
            elif current_user.is_authenticated and current_user.role == 'Admin' and role == 'User':
                return func(*args, **kwargs)
            # Role yg akses User, kalo require User, dia lolos
            elif current_user.is_authenticated and role == 'User' and current_user.role == 'User':
                return func(*args, **kwargs)
            # Role yg akses User, kalo require Admin, dia gagal
            else:
                return { "message": "Unauthorized" }, 403    
            #admin and user have different permissions liatnya beda page 
            #admin has higher permissions than user misalnya bisa create dan edit

        return wrapper
    return decorator

