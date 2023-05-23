from flask_login import UserMixin
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from src.db.db_config import Base, engine
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from datetime import datetime

class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    username = Column(String(64), nullable=False, index=True, unique=True)
    password = Column(String(128), nullable=False)
    role = Column(String(64), nullable=False, unique=False)
    email = Column(String(128), index=True, unique=True, nullable=True)
    name = Column(String(50), nullable=True, unique=False)
    surname = Column(String(50), nullable=True, unique=False)
    created = Column(DateTime, default=datetime.utcnow(), nullable=False)
    modified = Column(DateTime, default=datetime.utcnow(), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    @property
    def is_superuser(self):
        return self.role == 'superuser'
    
    access_history = relationship('AccessHistory', backref='user')

    def __repr__(self):
        return f'''<User {self.username}, Role: {self.role}> '''


class AccessHistory(Base):
    __tablename__ = 'access_history'
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.id), index=True)
    action = Column(String(128), unique=False, nullable=False)
    created = Column(DateTime, default=datetime.utcnow(), nullable=False)

    def __repr__(self):
        return f'''<User {self.user_id}, Action: {self.action}, Created: {self.created}> '''


class Role(Base):
    __tablename__ = 'roles'
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    role_name = Column(String(64), unique=True, index=True, nullable=False)
    created = Column(DateTime, default=datetime.utcnow(), nullable=False)
    modified = Column(DateTime, default=datetime.utcnow(), nullable=False)

    def __repr__(self):
        return f'''<Role {self.role_name}, ID: {self.id}, Created: {self.created}> '''

class Right(Base):
    __tablename__ = 'rights'
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    right_name = Column(String(64), unique=True, index=True, nullable=False)
    created = Column(DateTime, default=datetime.utcnow(), nullable=False)
    modified = Column(DateTime, default=datetime.utcnow(), nullable=False)
    
    def __repr__(self):
        return f'''<Right {self.right_name}, ID: {self.id}, Created: {self.created}> '''

class RoleRight(Base):
    __tablename__ = 'role_rights'
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey(Role.id), index=True)
    right_id = Column(UUID(as_uuid=True), ForeignKey(Right.id), index=True)
    created = Column(DateTime, default=datetime.utcnow(), nullable=False)


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)