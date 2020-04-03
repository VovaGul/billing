from architecture.DetailingClient import DetailingClient
from architecture.files_analyzers import give_operation_this_number
from architecture.Client import Client


def get_client_type(detailing):
    """определяет какой класс клиента нужен"""
    if detailing:
        return DetailingClient
    return Client


def give_clients(numbers, client_type, path_logs, t_start, t_end):
    """записывает номера и информацию о них"""
    clients = {}
    for num, date, date_end, operation, coef in give_operation_this_number(numbers, path_logs, t_start, t_end):
        clients\
            .setdefault(num, client_type(num))\
            .append_score_and_details(date, date_end, operation, coef)

    for num in clients:
        clients[num].add_general_score()

    return clients


def give_bills(clients):
    """возвращает билль"""
    bill = []
    for num in clients:
        bill.extend(clients[num].bill)
    return "".join(bill)
