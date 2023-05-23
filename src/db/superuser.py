from src.db.db_config import db_session
from src.db.model import User, Role
from src.core.config import settings
from src.db.db_config import Base
from src.db.model import User, Role

def create_superuser():
    superuser = User.query.filter_by(is_superuser=True).first()
    if not superuser:
        superuser_role = Role.query.filter_by(role_name='superuser').first()
        if not superuser_role:
            superuser_role = Role(role_name='superuser')
            db_session.add(superuser_role)
            db_session.commit()

        
        superuser = User(
            username=settings.superuser_name,
            role=superuser_role.role_name,
            name='Arnold',
            surname='Shortman',
            email='heyarnold@gmail.com'
        )
        superuser.set_password(settings.superuser_pass)

        db_session.add(superuser)
        db_session.commit()


if __name__ == '__main__':
    create_superuser()
