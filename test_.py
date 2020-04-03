import unittest

from datetime import datetime, timedelta
from decimal import Decimal

from architecture.Client import Client, Rate
from architecture.DetailingClient import DetailingClient
from architecture.files_analyzers import give_rates_desc, Rate_desc, give_services_desc, Serv_desc,\
    give_operation_this_number
from architecture.get_night_time import get_count_nights, get_night_time_for_full_days, get_night_time, add_morning_time
from architecture.work_with_files import IteratorFile, read_file, write_file
from architecture.date_parse import get_period, check_period, get_default, parse_date
from architecture.work_with_paths import put_memory_path
from architecture.billing import get_client_type


class TestCase(unittest.TestCase):
    @staticmethod
    def look_matches(ans, r_answer):
        iter_right = iter(r_answer)
        iter_ans = iter(ans)
        for elem in iter_right:
            for word in iter_ans:
                if word == elem:
                    break
            else:
                return [w for w in iter_right]

    # billing.py
    def test_get_client_type(self):
        self.func_get_client_type(Client, False)
        self.func_get_client_type(DetailingClient, True)

    def func_get_client_type(self, right_answer, detailing):
        self.assertEqual(right_answer, get_client_type(detailing))

    # Client.py
    def test_append_exits_limited_option(self):
        rate = Rate('A', datetime(2018, 1, 1), datetime(2018, 2, 1), {"B": 12})
        self.assertEqual(0, Client(0).append_exits_limited_option(rate, "B", Decimal(12)))

    def test_append_score_and_details(self):
        Client.set_client_attrs({"A": Rate_desc((Decimal(1)), timedelta(days=30), {"CALL": 12})},
                                {'CALL': Serv_desc("", Decimal(-1), Decimal(-1), False, False, False)})
        client = Client(0)
        client.append_score_and_details(datetime(2018, 1, 1, 1, 1, 1), datetime(2018, 1, 1, 1, 1, 10),
                                        "CALL", Decimal("9"))
        self.assertEqual(Decimal('-2'), client.score)

    # date_parse.py
    def test_get_period(self):
        self.assertEqual(get_period("2010-01-01", '2010-01-09 13:05'),
                         (datetime(2010, 1, 1, 0, 0), datetime(2010, 1, 9, 13, 5)))

    def test_check_period(self):
        self.assertEqual(check_period(datetime(2010, 1, 1, 0, 0), datetime(2010, 1, 9, 13, 5)), None)

    def test_get_default(self):
        self.func_get_default(datetime.max, None)
        self.func_get_default(datetime(2010, 1, 1, 0, 0), datetime(2010, 1, 1, 0, 0))

    def func_get_default(self, answer, date):
        self.assertEqual(get_default(datetime.max, date), answer)

    def test_parse_date(self):
        self.func_parse_date(None, None)
        self.func_parse_date(datetime(2010, 1, 1, 0, 0), "2010-01-01")

    def func_parse_date(self, answer, str_date):
        self.assertEqual(parse_date(str_date), answer)

    # files_analyzars
    def test_give_rates_desc(self):
        self.assertEqual(give_rates_desc('Test_files/test_give_rates_desc/rates_long_time.txt'),
                         {'UNLIMITED_INTERNET': Rate_desc(price=Decimal('-300'),
                                                          time=timedelta(3000), options={'INTERNET': -1})})

    def test_give_services_desc(self):
        self.assertEqual(give_services_desc('Test_files/test_give_services_desc/services_description.txt'),
                         {'CALL': Serv_desc(unit='c', coef=Decimal('-0.01'), coef_n=Decimal('-0.005'), evening=True,
                                            night=True, morning=False),
                          'INTERNET': Serv_desc(unit='MB', coef=Decimal('-1'), coef_n=None, evening=False, night=False,
                                                morning=False),
                          'SMS': Serv_desc(unit='sms', coef=Decimal('-1'), coef_n=None, evening=True, night=False,
                                           morning=True)})

    def test_give_operation_this_number(self):
        answer = [line for line in give_operation_this_number('89820000002', 'Test_files/test_give_operation_'
                                                                             'this_number/logs.txt',
                                                              datetime(2010, 1, 1), datetime(2011, 1, 1, 7))]
        self.assertEqual(answer, [('89820000002', datetime(2010, 1, 1, 5, 59, 55), datetime(2010, 1, 1, 6, 0, 2),
                                   'CALL', Decimal('7')), ('89820000002', datetime(2010, 1, 1, 5, 59, 55),
                                                           datetime(2010, 1, 1, 6, 0, 2), 'CALL',
                                                           Decimal('9'))])

    # get_night_time.py
    def test_get_count_nights(self):
        self.func_get_count_nights(0, 1)
        self.func_get_count_nights(1, 2)
        self.func_get_count_nights(9, 10)
        self.func_get_count_nights(0, 0)

    def func_get_count_nights(self, right_answer, count_days):
        self.assertEqual(right_answer, get_count_nights(count_days))

    def test_get_night_time_for_full_days(self):
        self.func_get_night_time_for_full_days(timedelta(hours=6), datetime(2018, 1, 1), datetime(2018, 1, 3), False)
        self.func_get_night_time_for_full_days(timedelta(hours=0), datetime(2018, 1, 1), datetime(2018, 1, 2), False)
        self.func_get_night_time_for_full_days(timedelta(hours=18), datetime(2018, 1, 1), datetime(2018, 1, 5), False)
        self.func_get_night_time_for_full_days(timedelta(hours=42), datetime(2018, 1, 1), datetime(2018, 1, 3), True)
        self.func_get_night_time_for_full_days(timedelta(hours=18), datetime(2018, 1, 1), datetime(2018, 1, 2), True)
        self.func_get_night_time_for_full_days(timedelta(hours=90), datetime(2018, 1, 1), datetime(2018, 1, 5), True)

    def func_get_night_time_for_full_days(self, right_answer, start, end, night):
        self.assertEqual(right_answer, get_night_time_for_full_days(start, end, night))

    def test_get_night_time(self):
        self.func_get_night_time(timedelta(hours=0), datetime(2018, 1, 1, 6), datetime(2018, 1, 2),
                                 False, False, False)
        self.func_get_night_time(timedelta(hours=6), datetime(2018, 1, 1), datetime(2018, 1, 1, 6),
                                 False, False, False)
        self.func_get_night_time(timedelta(hours=6), datetime(2018, 1, 1, 23), datetime(2018, 1, 2, 6),
                                 False, False, False)
        self.func_get_night_time(timedelta(hours=6), datetime(2018, 1, 1), datetime(2018, 1, 1, 7),
                                 False, False, False)
        self.func_get_night_time(timedelta(hours=2), datetime(2018, 1, 1, 3), datetime(2018, 1, 1, 5),
                                 False, False, False)
        self.func_get_night_time(timedelta(hours=12), datetime(2018, 1, 1), datetime(2018, 1, 3),
                                 False, False, False)
        self.func_get_night_time(timedelta(hours=18), datetime(2018, 1, 1), datetime(2018, 1, 3, 7),
                                 False, False, False)
        self.func_get_night_time(timedelta(hours=17), datetime(2018, 1, 1), datetime(2018, 1, 3, 5),
                                 False, False, False)
        self.func_get_night_time(timedelta(hours=17), datetime(2018, 1, 1), datetime(2018, 1, 3, 5),
                                 False, False, False)
        self.func_get_night_time(timedelta(hours=13), datetime(2018, 1, 1, 23), datetime(2018, 1, 3, 7),
                                 True, False, False)
        self.func_get_night_time(timedelta(hours=31), datetime(2018, 1, 1, 23), datetime(2018, 1, 3, 7),
                                 True, True, False)
        self.func_get_night_time(timedelta(hours=30), datetime(2018, 1, 1, 23), datetime(2018, 1, 3, 7),
                                 False, True, False)
        self.func_get_night_time(timedelta(hours=13), datetime(2018, 1, 1, 23), datetime(2018, 1, 3, 7),
                                 False, False, True)
        self.func_get_night_time(timedelta(hours=14), datetime(2018, 1, 1, 23), datetime(2018, 1, 3, 7),
                                 True, False, True)
        self.func_get_night_time(timedelta(hours=32), datetime(2018, 1, 1, 23), datetime(2018, 1, 3, 7),
                                 True, True, True)

    def func_get_night_time(self, right_answer, start, end, morning, night, evening):
        self.assertEqual(right_answer, get_night_time(start, end, morning, night, evening))

    # work_with_files.py
    def test_read_file(self):
        self.assertEqual(read_file('Test_files/test_read_file/path.txt'), 'Test_files/test_read_file/path.txt')

    def test_IteratorFile(self):
        answer = [line for line in IteratorFile('Test_files/test_read_file/path.txt')]
        self.assertEqual(''.join(answer), "Test_files/test_read_file/path.txt")

    # work_with_paths.py
    def test_put_memory_path(self):
        self.func_put_memory_path('Test_files/test_read_file/path.txt', None)
        content = read_file('Test_files/test_read_file/path.txt')
        self.func_put_memory_path('Test_files/logs.txt', 'Test_files/logs.txt')
        write_file('Test_files/test_read_file/path.txt', content)

    def func_put_memory_path(self, right_answer, path_file):
        self.assertEqual(right_answer, put_memory_path('Test_files/test_read_file/path.txt', path_file))


if __name__ == '__main__':
    unittest.main()
