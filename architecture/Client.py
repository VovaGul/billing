from collections import namedtuple
from copy import deepcopy
from datetime import timedelta
from decimal import Decimal
from enum import Enum

from architecture.get_night_time import get_night_time

Rate = namedtuple('Rate', 'name start end options')


class WordsForDetailing(Enum):
    CURRENCY = "руб"
    TARIFF_IS_CONNECTED = "#  ТАРИФ ПОДКЛЮЧЕН"
    TOTAL = "всего"
    NIGHT_RATE = "НОЧНОЙ"
    DAY_RATE = "ДНЕВНОЙ"


class Client:
    """информация о номере, полученная из логов"""
    rates_desc = None
    services_desc = None

    def __init__(self, number, rates=list()):
        self.bill = [number, ":\n"]
        self.score = 0
        self.rates = rates

    @staticmethod
    def set_client_attrs(rates_desc, services_desc):
        """устанавливает значения для аттрибутов класса"""
        Client.rates_desc = rates_desc
        Client.services_desc = services_desc
        Client.there_are_common_names()

    @staticmethod
    def there_are_common_names():
        """проверяет на отсутствие общих имен у тарифов и опций"""
        common = set(Client.rates_desc) & set(Client.services_desc)
        if common:
            raise ValueError("имеются общие имена у тарифов и сервисов {}".format(common))

    def add_rate(self, date, operation):
        """добавляет очередной тариф в 'rates'"""
        start = date
        end = start + self.rates_desc[operation].time
        self.rates.append(Rate(operation, start, end, deepcopy(self.rates_desc[operation].options)))

    def append_exists_unlimited_option(self):
        """добавляет счет за услугу входящую в безлимитный тариф"""
        pass

    def append_exits_limited_option(self, rate, operation, coef):
        """добавляет счет за услугу входящую в лимитный тариф"""
        rate.options[operation] -= coef
        if rate.options[operation] < 0:
            score = -rate.options[operation]
            rate.options[operation] = 0
            return score
        return 0

    def append_service_in_rate(self, rate, operation, coef):
        """добавляет счет за услугу, на которую распространяется тариф"""
        if rate.options[operation] == -1:
            self.append_exists_unlimited_option()
            return 0
        if rate.options[operation] > 0:
            return self.append_exits_limited_option(rate, operation, coef)

    @staticmethod
    def get_quantity_coef_used_at_night(date, date_end, coef, evening, night, morning):
        """возвращает количество коэффициента, использованного ночью"""
        time_operation = date_end - date
        if time_operation == timedelta(0):
            return 0
        return coef * (Decimal(get_night_time(date, date_end, morning, night, evening).total_seconds()) /
                       Decimal(time_operation.total_seconds()))

    def give_score_service(self, coef_service, coef, day_period):
        """возвращает счет за услугу"""
        score_oper = 0
        if coef:
            score_oper = coef_service * coef
        return score_oper

    @staticmethod
    def get_residual_coef(coef, date, date_end, rate_end):
        """возвращает коэффициент, оставшийся после срока окончания тарифа"""
        try:
            residual_coef = coef * (Decimal((date_end - rate_end).total_seconds()) /
                                    Decimal((date_end - date).total_seconds()))
            if residual_coef < 0:
                residual_coef = 0
        except ZeroDivisionError:
            residual_coef = 0

        return residual_coef

    @staticmethod
    def get_rate_end(coef, date, date_end, not_used_coef, rate_end):
        """возвращает время, в которое закончилась предоставляемая тарифом услуга"""
        if not_used_coef:
            service_time = Decimal((date_end - date).total_seconds())
            rate_delta_sec = service_time * ((coef - not_used_coef) / coef)
            rate_delta = timedelta(milliseconds=int(rate_delta_sec * Decimal("1e+3")))
            rate_end = date + rate_delta

        return rate_end

    def search_and_append_sevice_in_rate(self, date, operation, date_end, coef):
        """списывает коэффициент услуги с тарифов. Возвращает оставшийся коэффициент и время,
         в которое тариф окончил предоставление услуги"""
        rate_end = date
        services_is_in_rates = True
        while services_is_in_rates and \
                coef:
            for rate in self.rates:
                if rate.start <= date <= rate.end and \
                        operation in rate.options and \
                        rate.options[operation] != 0:
                    rate_end = rate.end
                    residual_coef = self.get_residual_coef(coef, date, date_end, rate.end)
                    not_used_coef = self.append_service_in_rate(rate, operation, coef - residual_coef)
                    rate_end = self.get_rate_end(coef, date, date_end, not_used_coef, rate_end)
                    coef = not_used_coef
                    break
            else:
                services_is_in_rates = False
        return rate_end, coef

    def get_service_to_main_plan(self, service_desc, date, date_end, coef):
        """возвращает счет за услугу по основному плану"""
        night_coef = self.get_quantity_coef_used_at_night(date, date_end, coef,
                                                          service_desc.evening,
                                                          service_desc.night,
                                                          service_desc.morning)
        score_oper = self.give_score_service(service_desc.coef_n, night_coef, WordsForDetailing.NIGHT_RATE.value)
        score_oper += self.give_score_service(service_desc.coef, coef, WordsForDetailing.DAY_RATE.value)

        return score_oper

    def give_rate_score(self, operation, coef, date):
        """возвращает счет за тариф"""
        score_oper = self.rates_desc[operation].price * coef
        return score_oper

    def append_score_and_details(self, date, date_end, operation, coef):
        """добавляет счет за тариф или услугу"""
        if operation in self.rates_desc:
            self.add_rate(date, operation)
            self.score += self.give_rate_score(operation, coef, date)
            return
        if operation in self.services_desc:
            date, coef = self.search_and_append_sevice_in_rate(date, operation, date_end, coef)
            self.score += self.get_service_to_main_plan(self.services_desc[operation], date, date_end, coef)
            return
        raise ValueError("неивестная операция: {}".format(operation))

    def add_general_score(self):
        """дописывает итоговую сумму в счет пользователя"""
        self.bill.append("{} {} {}\n".format(WordsForDetailing.TOTAL.value,
                                             str(self.score), WordsForDetailing.CURRENCY.value))
