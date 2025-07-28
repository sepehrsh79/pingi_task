from .models import BaseUser, UserStats


def get_user(*, user_id:int) -> BaseUser:
    user = BaseUser.objects.get(id=user_id)
    return user


def get_or_create_user_stats(*, user_id:int) -> tuple:
    stats, _ = UserStats.objects.get_or_create(user=get_user(user_id=user_id))
    return stats, _


def get_user_with_mobile(*, mobile:int) -> BaseUser:
    user = BaseUser.objects.get(mobile=mobile)
    return user


def get_stats_with_user(*, user:BaseUser) -> UserStats:
    stats = UserStats.objects.get(user=user)
    return stats

