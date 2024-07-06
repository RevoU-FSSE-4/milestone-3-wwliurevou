from models.base import Base
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import mapped_column

from sqlalchemy.sql import func

class Accounts(Base):
    __tablename__ = 'accounts' #diisi table dari mysql
    user_id = mapped_column(Integer)
    # diisi kolom-kolom yang ada di table ini
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    account_type = mapped_column(String(255), nullable=False)
    account_number = mapped_column(String(255), unique=True, autoincrement=True)
    balance = mapped_column(DECIMAL(10,2), nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.utc_timestamp())

    # Relationship List
    # reviews = relationship("Review", cascade="all,delete-orphan")

    def __repr__(self):
        return f'<Accounts {self.name}>'