import logging
import secrets
from datetime import UTC, datetime, timedelta

from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from core.config import settings

logger= logging.getLogger(__name__)


password_context= CryptContext(schemes=["argon2"], deprecated= "auto")




def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(plain: str, password: str) -> str:
    return password_context.verify(plain, password)


def generate_otp() -> str :
    code= str(secrets.token_hex(4))
    return code


def create_email_verification_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(hours=settings.EMAIL_VERIFICATION_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire, "type": "verify_email"})
    return jwt.encode(to_encode, settings.SECRET_KEY.get_secret_value(), algorithm=settings.ALGORITHM)


def create_access_token(data: dict) -> str:
    to_encode= data.copy()
    expire= datetime.now(UTC) + timedelta(minutes= settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type":"access"})
    return jwt.encode(to_encode, settings.SECRET_KEY.get_secret_value(), algorithm= settings.ALGORITHM)


def create_password_reset_token(data: dict) -> str:
    to_encode= data.copy()
    expire= datetime.now(UTC) + timedelta(minutes= settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type":"password_reset"})
    return jwt.encode(to_encode, settings.SECRET_KEY.get_secret_value(), algorithm= settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode= data.copy()
    expire= datetime.now(UTC) + timedelta(days= settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY.get_secret_value(), algorithm= settings.ALGORITHM)
    
 
def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY.get_secret_value(), algorithms=[settings.ALGORITHM])
    except ExpiredSignatureError as e:
        logger.warning(f"Expired token: {e}")
        raise ValueError("Token has expired")
    
    except JWTError as e:
        logger.warning(f"Invalid token: {e}")
        raise ValueError("Invalid token")
    
    return payload
