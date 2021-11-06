import time


def f():
    t0 = time.time_ns()
    time.sleep(.01)
    return str(time.time_ns() - t0)


def g():
    t0 = time.time_ns()
    time.sleep(10)
    return str(time.time_ns() - t0)


def h():
    t0 = time.time_ns()
    x = 246912457
    for i in range(x-1, 1, -1):
        if (x % i) == 0:
            break
    return str(time.time_ns() - t0)

def hb():
    t0 = time.time_ns()
    x = 24699
    for i in range(x-1, 1, -1):
        if (x % i) == 0:
            break
    return str(time.time_ns() - t0)
