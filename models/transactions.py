from models.base import Base
from sqlalchemy import DECIMAL, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func

class Transactions(Base):
    __tablename__ = 'transactions'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_account_id = mapped_column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    to_account_id = mapped_column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    amount = mapped_column(DECIMAL(10,2),nullable=False)
    type = mapped_column(String(255)) #gimana caranya bikin ini cmn certain types doang
    description = mapped_column(Text)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.utc_timestamp())
    def __repr__(self):
        return f'<Transactions {self.id}>'