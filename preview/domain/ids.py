import secrets


def new_session_id() -> str:
    return secrets.token_hex(16)


def new_action_token() -> str:
    return secrets.token_urlsafe(24)
