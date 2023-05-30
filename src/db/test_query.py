from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from src.db.db_config import Base, engine, db_session
from src.db.model import User, AccessHistory, Role, UserRole
from src.core.config import settings

db_uri = f'postgresql://{settings.db_user}:{settings.db_password}@localhost:{settings.db_port}/{settings.db_name}'

engine = create_engine(db_uri)
db_session = scoped_session(sessionmaker(bind=engine))


if __name__ == '__main__':
    user_id = '67132751-a3fe-4204-8fc4-c48d7c36f2d4'
    u_r = db_session.query(UserRole).filter(UserRole.user_id == user_id).first()
    role = db_session.query(Role).filter(Role.id == u_r.role_id).first()

    user_roles = db_session.query(User).filter(User.id == user_id).first()
    roles = [role.role_name for role in user_roles.roles]

    print('Hello world')