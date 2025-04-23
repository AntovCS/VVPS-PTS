import bcrypt
from datetime import datetime, timedelta

class Security:
    failed_attempts = 0
    lockout_until = None
    LOCKOUT_DURATION = 300
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD_HASH = bcrypt.hashpw("123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(password, hashed):
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    @classmethod
    def is_locked_out(cls):
        if cls.lockout_until and datetime.now() < cls.lockout_until:
            remaining = (cls.lockout_until - datetime.now()).seconds
            print(f"Too many failed attempts. Try again in {remaining} seconds.")
            return True
        if cls.lockout_until and datetime.now() >= cls.lockout_until:
            cls.reset_lockout()
        return False

    @classmethod
    def reset_lockout(cls):
        cls.failed_attempts = 0
        cls.lockout_until = None