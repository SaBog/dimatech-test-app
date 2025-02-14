from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Numeric,
    String,
    Integer,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    balance = Column(Numeric(precision=12, scale=2), default=0.0, nullable=False)

    user = relationship("User", back_populates="accounts")
    payments = relationship(
        "Payment", back_populates="account", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<Account(id={self.id}, user_id={self.user_id}, balance={self.balance})>"
        )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    accounts = relationship(
        "Account", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, is_admin={self.is_admin})>"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, nullable=False)
    account_id = Column(
        Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    amount = Column(Numeric(precision=12, scale=2), default=0.0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    account = relationship("Account", back_populates="payments")

    def __repr__(self):
        return f"<Payment(id={self.id}, transaction_id={self.transaction_id}, amount={self.amount})>"
