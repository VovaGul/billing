import argparse
from sys import stderr, exit

from architecture.billing import get_client_type, give_clients,give_bills
from architecture.files_analyzers import give_rates_desc, give_services_desc
from architecture.work_with_paths import put_memory_path
from architecture.date_parse import get_period
from architecture.saved_paths import RATES_DESC, LOGS, SERVICES_DESC

ERROR_WRONG_SETTINGS = 1


def parse_args():
    """Разбор аргументов запуска"""
    parser = argparse.ArgumentParser(description="счета для каждого из пользователей с возможностью детализации")
    parser.add_argument('-n', dest='numbers', metavar='N', nargs='*', help='номер абонента')
    parser.add_argument('-d', action='store_true', dest='detailing', help='детализация счета')
    parser.add_argument('-l', dest='logs', help='запомнить новый путь до файла с логами')
    parser.add_argument('-od', dest='services_desc', help='запомнить новый путь до файла с описанием операций')
    parser.add_argument('-rd', dest='rates_desc', help='запомнить новый путь до файла с описанием тарифов')
    parser.add_argument('-st', dest='time_start', help='указать начало временного периода. Формат гггг-мм-дд*чч:мм:сс')
    parser.add_argument('-en', dest='time_end', help='указать конец временного периода. Формат гггг-мм-дд*чч:мм:сс')

    return parser.parse_args()


def main():
    """Точка входа в программу"""
    args = parse_args()

    path_logs = None
    path_rates_desc = None
    path_services_desc = None
    try:
        path_logs = put_memory_path(LOGS, args.logs)
        path_rates_desc = put_memory_path(RATES_DESC, args.rates_desc)
        path_services_desc = put_memory_path(SERVICES_DESC, args.services_desc)
    except FileNotFoundError as e:
        print(e, file=stderr)
        exit(ERROR_WRONG_SETTINGS)

    t_start = None
    t_end = None
    try:
        t_start, t_end = get_period(args.time_start, args.time_end)
    except ValueError as e:
        print(e, file=stderr)
        exit(ERROR_WRONG_SETTINGS)

    rates_desc = give_rates_desc(path_rates_desc)
    services_desc = give_services_desc(path_services_desc)
    client_type = get_client_type(args.detailing)
    client_type.set_client_attrs(rates_desc, services_desc)
    bill = None
    try:
        clients = give_clients(args.numbers, client_type, path_logs, t_start, t_end)
        bill = give_bills(clients)
    except AttributeError as e:
        print(e, file=stderr)
        exit(ERROR_WRONG_SETTINGS)
    except ValueError as e:
        print(e, file=stderr)
        exit(ERROR_WRONG_SETTINGS)

    print(bill)


if __name__ == "__main__":
    main()
