from datetime import timedelta, datetime
from enum import Enum


class LenOfDay(Enum):
    """количество часов, которое идет время суток"""
    NIGHT = 6
    DAY = 18


def get_count_nights(count_days):
    """возвращает количество ночей, имея количество дней"""
    if count_days:
        count_days -= 1
    return count_days


def get_night_time_for_full_days(start, end, night):
    """возвращает ночное время между дневным временем"""
    night_time = timedelta(0)
    count_days = (datetime(end.year, end.month, end.day) - datetime(start.year, start.month, start.day)).days
    if night:
        night_time += timedelta(hours=count_days * LenOfDay.DAY.value)
    night_time += timedelta(hours=get_count_nights(count_days) * LenOfDay.NIGHT.value)
    return night_time


def add_morning_time(end, morning):
    """возвращает время за последнее утро"""
    if morning:
        if end.hour > LenOfDay.NIGHT.value:
            last_night_end = datetime(end.year, end.month, end.day, LenOfDay.NIGHT.value)
            return end - last_night_end
    return timedelta(0)


def get_time_for_last_night(start, end):
    """возвращает время за последнюю ночь"""
    last_night_start = datetime(end.year, end.month, end.day, 0)
    if last_night_start > start:
        if end.hour < LenOfDay.NIGHT.value:
            return end - last_night_start
        return timedelta(hours=LenOfDay.NIGHT.value)
    return timedelta(0)


def get_night_time_for_last_day(start, end, morning):
    """считает ночное время за первую ночь и последние сутки"""
    night_time = timedelta(0)
    first_night_end = datetime(start.year, start.month, start.day, LenOfDay.NIGHT.value)
    if first_night_end < end:
        night_time += first_night_end - start
        night_time += add_morning_time(end, morning)
        night_time += get_time_for_last_night(start, end)
    else:
        night_time += end - start

    return night_time


def get_night_time(start, end, morning, night, evening):
    """возвращает суммарное ночное время между start и end.
     morning, night, evening - модификаторы, влияющие на то,
      какое время считать ночным"""
    night_time = timedelta(0)

    """считает ночное время за первый вечер"""
    if start.hour >= LenOfDay.NIGHT.value:
        next_night = datetime(start.year, start.month, start.day + 1)
        if end <= next_night:
            return night_time
        if evening:
            night_time += next_night - start
        start = next_night

    night_time += get_night_time_for_full_days(start, end, night)
    night_time += get_night_time_for_last_day(start, end, morning)

    return night_time
