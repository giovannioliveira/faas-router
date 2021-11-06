import time


def f():
    print('executing f locally')
    t0 = time.time_ns()
    time.sleep(.01)
    return str(time.time_ns() - t0)


def g():
    print('executing g locally')
    t0 = time.time_ns()
    time.sleep(10)
    return str(time.time_ns() - t0)


def h():
    print('executing h locally')
    t0 = time.time_ns()
    x = 24691245
    for i in range(x-1, 1, -1):
        if (x % i) == 0:
            break
    return str(time.time_ns() - t0)

def hb():
    print('executing hb locally')
    t0 = time.time_ns()
    x = 24691245
    for i in range(x-1, 1, -1):
        if (x % i) == 0:
            break
    return str(time.time_ns() - t0)
