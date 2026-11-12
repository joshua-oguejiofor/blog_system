import redis.asyncio as redis

from .config import settings

redis_client = redis.from_url(
    settings.REDIS_URL, 
    decode_responses=True,
    socket_timeout=5,  # Set a timeout for socket operations
    socket_connect_timeout=5,  # Set a timeout for socket connections
    retry_on_timeout=True,  # Retry on timeout
    health_check_interval=30,  # Perform health checks every 30 seconds
)

async def get_redis():
    return redis_client


async def set_cache(key: str, expire: int, value: str):
    await redis_client.setex(key, expire, value)


async def increment_post(post_id: int, user_id: int):
    key= f"user_id:{user_id}-post:{post_id}:views"
    return await redis_client.incr(key)
    

async def get_cache(key: str):
    return await redis_client.get(key)


async def delete_cache(key: str):
    await redis_client.delete(key)


async def set_refresh_token(user_id: str, expire_minutes: int, token: str):
    key = f"refresh:{user_id}"
    await redis_client.setex(key, expire_minutes, token)


async def get_refresh_token(user_id: str):
    return await redis_client.get(f"refresh:{user_id}")


#store otp for forget password
async def set_otp(email: str, expire_minutes: int, otp: str):
    key = f"otp:{email}"
    await redis_client.setex(key, expire_minutes * 60, otp)

#get otp for forget password
async def get_otp(email: str):
    return await redis_client.get(f"otp:{email}")

#this is to blacklist a access token
async def invalidate_token(token: str, expire: int = 86400):
    await redis_client.setex(f"blacklist:{token}", expire, "1")

#check if the access token is blacklisted
async def is_token_blacklisted(token: str) -> bool:
    return await redis_client.exists(f"blacklist:{token}") == 1


