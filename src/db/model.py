from datetime import datetime
import uuid

from flask_login import UserMixin
from sqlalchemy import Column, ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from src.db.db_config import Base, engine


class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    username = Column(String(64), nullable=False, index=True, unique=True)
    password = Column(String(128), nullable=False)
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
    roles = relationship('Role', secondary='user_roles', backref='users')

    def __repr__(self):
        return f'''<User {self.username}, Name: {self.name}, Surname: {self.surname}, Email: {self.email}>'''


class Role(Base):
    __tablename__ = 'roles'
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    role_name = Column(String(64), unique=True, index=True, nullable=False)
    created = Column(DateTime, default=datetime.utcnow(), nullable=False)
    modified = Column(DateTime, default=datetime.utcnow(), nullable=False)

    def __repr__(self):
        return f'''<Role {self.role_name}, ID: {self.id}, Created: {self.created}> '''


class UserRole(Base):
    __tablename__ = 'user_roles'
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.id), index=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey(Role.id), index=True)


class AccessHistory(Base):
    __tablename__ = 'access_history'
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.id), index=True)
    action = Column(String(128), unique=False, nullable=False)
    created = Column(DateTime, default=datetime.utcnow(), nullable=False)

    def __repr__(self):
        return f'''<User {self.user_id}, Action: {self.action}, Created: {self.created}> '''


class Alembic(Base):
    __tablename__ = 'alembic_version'
    version_num = Column(String(32), primary_key=True)


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
