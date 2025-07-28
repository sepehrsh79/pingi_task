import redis
import random
import logging
from config import settings

logger = logging.getLogger(__name__)

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)


def limit_otp(mobile: str) -> bool:
    existing_otp = redis_client.get(f"otp:{mobile}")
    ttl = redis_client.ttl(f"otp:{mobile}") if existing_otp else 0
    if existing_otp and ttl > 0:
        logger.info(f"OTP [{mobile}] -> [{existing_otp}]")
        return True
    return False

def generate_and_store_otp(mobile: str) -> str:
    otp = str(random.randint(100000, 999999))
    redis_client.setex(f"otp:{mobile}", 300, otp)
    logger.info(f"OTP [{mobile}] -> [{otp}]")
    return otp

def verify_otp(mobile: str, otp: str) -> bool:
    stored_otp = redis_client.get(f"otp:{mobile}")
    if stored_otp and stored_otp == otp:
        redis_client.delete(f"otp:{mobile}")
        return True
    return False

