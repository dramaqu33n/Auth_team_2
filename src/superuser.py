from src.core.config import settings
from src.db.db_config import db_session
from src.db.model import User, Role, UserRole
from src.logs.log_config import logger
import click
from src.app import app


def create_basic_roles(basic_roles: list[str] = ['superuser', 'admin', 'user', 'guest']):
    '''Creating basic role types in initial db'''
    for role_name in basic_roles:
        role = db_session.query(Role).filter_by(role_name=role_name).first()
        if role:
            logger.info('Role %s exists', role_name)
            continue
        role = Role(role_name=role_name)
        db_session.add(role)
        db_session.commit()
        logger.info('Role %s created', role_name)

@app.cli.command("create_superuser")
def create_superuser() -> bool:
    '''There must be at least one superuser in our initial db'''
    superusername = click.prompt('Enter Username')
    name = click.prompt('Enter Name')
    surname = click.prompt('Enter Surname')
    email = click.prompt('Enter Email')
    password = click.prompt('Enter Password', hide_input=True)
    
    superuser_role = db_session.query(Role).filter_by(role_name='superuser').first()
    if not superuser_role:
        logger.critical('Create superuser role first in Role model')
        raise ValueError
    superuser_role_id = superuser_role.id
    superuser = db_session.query(UserRole).filter_by(role_id=superuser_role_id).first()
    
    if superuser:
        logger.info(f'Superuser with user id: {superuser.user_id} already exists')
        return False
    superuser = User(
        username=superusername,
        name=name,
        surname=surname,
        email=email
    )

    superuser.set_password(password)
    logger.info('Superuser %s created', superuser)
    db_session.add(superuser)
    db_session.commit()
    superuser_role = UserRole(
        user_id=superuser.id,
        role_id=superuser_role_id
        )
    db_session.add(superuser_role)
    db_session.commit()
    return True


if __name__ == '__main__':
    # create_basic_roles()
    create_superuser()
