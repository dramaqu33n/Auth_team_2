import pytest
from flask import json

from src.app import app
from src.db.db_config import db_session
from src.db.model import User
from src.logs.log_config import logger

# import your Flask app and db

def test_registration():
    tester = app.test_client()
    # make sure to change the data below according to your needs
    data = {
        'username': 'test_user',
        'password': 'test_password',
        'email': 'test@email.com',
        'name': 'Testen',
        'surname': 'Testenson',
    }
    logger.info('DATA: %s', data)
    response = tester.post('api/v1/auth/register', data=json.dumps(data), content_type='application/json')
    response_data = json.loads(response.data)
    assert response.status_code == 200
    assert response_data['message'] == 'User registered successfully'
    
    # cleanup: delete the test user we just created
    with app.app_context():
        test_user = db_session.query(User).filter_by(username='test_user').first()
        if test_user:
            db_session.delete(test_user)
            db_session.commit()
