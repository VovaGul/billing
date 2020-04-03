from enum import Enum
from re import compile
from collections import namedtuple
from datetime import timedelta
from decimal import Decimal

from architecture.work_with_files import IteratorFile
from architecture.date_parse import parse_date

Rate_desc = namedtuple('Rate_desc', 'price time options')
Serv_desc = namedtuple('Serv_desc', 'unit coef coef_n evening night morning')

R_LOG = compile(r'(\d{11}) (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) '
                r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) ([\w_]+)=?(\d*)\n?')
R_SERVICE = compile(r'([\w_]+) - (\w+) - (-?\d+\.?\d*) ?(-?\d+\.?\d*)* ?([()[\]n]*)[ \n]*')
OPTION_RE = compile(r'([\w_]+)=(-?\d+\.?\d*)[ \n]*')
NAME_RATES_RE = compile(r'([\w_]+) (-?\d+\.?\d*) (\d+)|([\w_]+) (-?\d+\.?\d*) (-?\d+\.?\d*) (\d+)')
RATES_RE = compile(r'(\d{11}) - ([\w_]+) - (\d{4}-\d{2}-\d{2}\*\d{2}:\d{2}:\d{2})')


class MODS(Enum):
    EVENING = '('
    NIGHT = 'n'
    MORNING = ')'


def give_operation_this_number(numbers, path_logs, t_start, t_end):
    """возвращает генератор по операциям"""
    for log in IteratorFile(path_logs):
        search = R_LOG.fullmatch(log)
        num, date_str, date_str_end, operation, coef = \
            search.group(1), search.group(2), search.group(3), search.group(4), search.group(5)
        date = parse_date(date_str)
        date_end = parse_date(date_str_end)
        if coef is "":
            coef = 1
        if (numbers is None or num in numbers) and t_start <= date <= t_end:
            yield num, date, date_end, operation, Decimal(coef)


def give_services_desc(path_services_desc):
    """возвращает описание услуг в виде словаря"""
    services_desc = {}
    service = None
    try:
        for service in IteratorFile(path_services_desc):
            res_search = R_SERVICE.fullmatch(service)
            if res_search is not None and bool(res_search.group(1)) is False:
                continue
            name, unit, coef, coef_n, mods = res_search.groups()
            if type(coef_n) is not str:
                coef_n = None
            else:
                coef_n = Decimal(coef_n)

            services_desc[name] = Serv_desc(unit, Decimal(coef), coef_n,
                                            MODS.EVENING.value in mods,
                                            MODS.NIGHT.value in mods,
                                            MODS.MORNING.value in mods)
    except AttributeError:
        raise AttributeError('строка не походит под шаблон для тарифа:{}\n'.format(service))
    return services_desc


def give_rates_desc(path_rates_desc):
    """возвращает описание тарифов в виде словаря"""
    rates_desc = {}
    rate_desc = None
    try:
        for rate_desc in IteratorFile(path_rates_desc):
            res_search = NAME_RATES_RE.match(rate_desc)
            name, price, time = res_search.group(1), res_search.group(2), res_search.group(3)
            options = {option[0]: int(option[1]) for option in OPTION_RE.findall(rate_desc)}
            rates_desc[name] = Rate_desc(Decimal(int(price)), timedelta(days=int(time)), options)
    except AttributeError:
        raise AttributeError('строка не походит под шаблон для тарифа:{}\n'.format(rate_desc))
    return rates_desc
