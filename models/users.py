from models.base import Base
from flask_login import UserMixin, current_user
from sqlalchemy.orm import mapped_column
from sqlalchemy import Integer, String, Text, DateTime, func
import bcrypt
class Users(Base, UserMixin):
    __tablename__ = 'users'
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    username = mapped_column(String(100), nullable=False)
    email = mapped_column(String(100), unique=True, nullable=False)
    password_hash = mapped_column(String(100), nullable=False) #harus di hash yakan
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    # role = mapped_column(String(100))
    updated_at = mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.utc_timestamp())
    ##need to encrypt password

    def set_password(self, password_hash):
        self.password_hash = bcrypt.hashpw(password_hash.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    ##compare password yang di hash 

    def check_password(self, password_hash):
        return bcrypt.checkpw(password_hash.encode('utf-8'), self.password_hash.encode('utf-8'))