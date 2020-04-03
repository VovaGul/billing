from architecture.Client import Client, WordsForDetailing


class DetailingClient(Client):
    """детализирует операции клиента"""

    def append_exists_unlimited_option(self):
        """добавляет счет за услугу входящую в безлимитный тариф
         и записывает детализацию"""
        self.bill.extend(('unlimited', '\n'))

    def search_and_append_service_in_rate(self, date, operation, date_end, coef):
        self.bill.extend("{} {} ".format(str(coef), self.services_desc[operation].unit))
        return super().search_and_append_sevice_in_rate(date, operation, date_end, coef)

    def append_exits_limited_option(self, rate, operation, coef):
        """добавляет счет за услугу входящую в лимитный тариф
         и записывает детализацию"""
        self.bill.extend("{}: {}={}".format(rate.name, operation, str(rate.options[operation])))
        coef_option = super().append_exits_limited_option(rate, operation, coef)
        remainder = -coef_option
        if remainder == 0:
            remainder = rate.options[operation]
        self.bill.extend("-{}={} ".format(str(coef), str(remainder)))
        return coef_option

    def get_service_to_main_plan(self, service_desc, date, date_end, coef):
        score_oper = super().get_service_to_main_plan(service_desc, date, date_end, coef)
        self.bill.append("\n")
        return score_oper

    def give_score_service(self, coef_service, coef, day_period):
        """возвращает счет за услугу"""
        score_oper = super().give_score_service(coef_service, coef, day_period)
        if coef:
            self.bill.extend("{}={} {} ".format(day_period, str(score_oper).rstrip('0').rstrip('.'),
                                                WordsForDetailing.CURRENCY.value))
        return score_oper

    def give_rate_score(self, operation, coef, date):
        """возвращает счет за тариф"""
        score_oper = super().give_rate_score(operation, coef, date)

        self.bill.append("{} {} {}\n".format(str(score_oper), WordsForDetailing.CURRENCY.value,
                                             WordsForDetailing.TARIFF_IS_CONNECTED.value))

        return score_oper

    def append_score_and_details(self, date, date_end, operation, coef):
        """добавляет счет за тариф или услугу
         и записывает детализацию"""
        self.bill.append("{} {} {} ".format(str(date), str(date_end), operation))

        super().append_score_and_details(date, date_end, operation, coef)
