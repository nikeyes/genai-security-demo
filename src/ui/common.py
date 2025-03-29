import time

def slow_echo(result):
    result = str(result)
    count = len(result)
    for i in range(count):
        time.sleep(0.0005)
        yield result[: i + 1]
