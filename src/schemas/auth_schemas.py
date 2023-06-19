register_schema = {
    "type": "object",
    "properties": {
        "username": {"type": "string"},
        "password": {"type": "string"},
        "email": {"type": "string"},
        "name": {"type": "string"},
        "surname": {"type": "string"},
        "role": {"type": "string"}
    },
    "required": ["username", "password", "email"]
}

login_schema = {
    "type": "object",
    "properties": {
        "username": {"type": "string"},
        "password": {"type": "string"},
    },
    "required": ["username", "password"]
}

password_reset_schema = {
    "type": "object",
    "properties": {
        "new_password": {"type": "string"},
    },
    "required": ["new_password"]
}
