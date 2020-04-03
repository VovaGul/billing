from datetime import timedelta, datetime
from random import randint, choice


nambers = []
def generator_log():
    data = datetime(2010, 1, 1)
    two_days = timedelta(days=1, hours=randint(0, 12), minutes=randint(0, 30), seconds=randint(0, 59))

    keys = ["CALL", "SMS", "INTERNET", "REFILL"]
    rr = ['UNLIMITED_CALL', 'UNLIMITED_INTERNET', '500SMS', 'CASUAL']

    # Смена количества логов тут
    for i in range(100):
        incoming = randint(89820000002, 89820000002)
        if incoming not in nambers:
            nambers.append(incoming)

        time_speaking = timedelta(seconds=randint(30, 100))

        rate = choice(keys)
        if randint(0, 100) <= 10:
            rate = choice(rr)
        if rate == "SMS":
            time_speaking = timedelta(seconds=1)
        time_speaking_str = '=' + str(time_speaking.seconds)
        if rate in rr:
            time_speaking_str = ''

        time_end = data

        if rate in ["CALL", "INTERNET"]:
            time_end += time_speaking

        yield ('{} {} {} {}{}').format(str(incoming), str(data), str(time_end), rate, time_speaking_str)

        data += two_days


with open(r"C:\Users\Никита\Desktop\ПЕТОН\Billing\Special_files\1logs.txt", 'w') as f:
    for log in generator_log():
        f.write(log + "\n")
    print("файл создан")

