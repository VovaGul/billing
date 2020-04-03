from datetime import datetime

formats_date = ["%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%Y-%m-%d %H",
                "%Y-%m-%d",
                "%Y-%m",
                "%Y"]


def parse_date(date_str):
    """переводит 'date_str' в формат 'datetime'"""
    if date_str is None:
        return
    er = None
    for format_d in formats_date:
        try:
            time = datetime.strptime(date_str, format_d)
            return time
        except ValueError as e:
            er = e
    raise er


def get_default(default, date):
    """выставяет переданное значение, если переменная равна 'None'"""
    if date is None:
        return default
    return date


def check_period(start, end):
    """проверяет период на корректность"""
    if start > end:
        raise ValueError("{} {}>{}".format("начало периода больше конца:", start, end))


def get_period(start, end):
    """возвращает период даты"""
    start = get_default(datetime.min, parse_date(start))
    end = get_default(datetime.max, parse_date(end))
    check_period(start, end)
    return start, end

