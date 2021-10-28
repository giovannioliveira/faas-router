import time


def f():
    time.sleep(.01)
    return "slept 10 ms"


def g():
    time.sleep(10)
    return "slept 10 s"


def h(x):
    for i in range(x-1, 1, -1):
        if (x % i) == 0:
            return False
    return True
