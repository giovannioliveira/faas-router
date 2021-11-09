import time
from flask import Flask, Response
import local
import urllib.request
import edge
import threading

app = Flask(__name__)

FNAME = 'faas-router-f'
GNAME = 'faas-router-g'
HBNAME = 'faas-router-hb'
HNAME = 'faas-router-h'

rcLock = threading.Lock()

remoteCount = {
    FNAME: 0,
    GNAME: 0,
    HNAME: 0,
    HBNAME: 0
}


def set_remote_count(newCountStr, fromAsync=False):
    rcLock.acquire()
    global remoteCount
    try:
        remoteCount = eval(newCountStr)
    except:
        print('error setting remote count')
    rcLock.release()
    print(('async ' if fromAsync else '') + 'set remote count: ', remoteCount)


def async_set_remote_count(newCountStr):
    threading.Thread(target=set_remote_count, args=(newCountStr,)).start()

def atomic_increment_remote_count(function_name,inc):
    rcLock.acquire()
    remoteCount[function_name] += inc
    rcLock.release()
    print("local remote count update: ", str(remoteCount))

def async_increment_remote_count(function_name, inc):
    threading.Thread(target=atomic_increment_remote_count, args=(function_name, inc)).start()

def reset_remote_count():
    set_remote_count(str({
        FNAME: 0,
        GNAME: 0,
        HNAME: 0,
        HBNAME: 0
    }))


def get_request(sufix):
    return urllib.request.urlopen("http://192.168.56.105:8080"+sufix, timeout=120).read().decode('utf-8')


def signal_remote_scale_up(function_name):
    try:
        set_remote_count(get_request("/"+function_name+"?wakeup=true"), True)
    except:
        print('async update failed for '+function_name)


def update_remote_count():
    errcnt = 0
    while True:
        try:
            set_remote_count(get_request("/info"))
            errcnt = 0
        except Exception as e:
            errcnt += 1
            if errcnt == 3:
                reset_remote_count()
            print('Error in connection with remote cloud', e)
        finally:
            time.sleep(.5)


def cloud_has_warm_instance(function_name):
    return True


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello, Goodbye.'


@app.route('/f')
def f():
    run_in_cloud = cloud_has_warm_instance(FNAME)
    error = False
    try:
        if run_in_cloud:
            print('running f cloud', str(remoteCount))
            async_increment_remote_count(FNAME, -1)
            res = None
            try:
                res = get_request("/f")
            except:
                pass
                # local.f()
                # error = False
                # run_in_cloud = False
            if res:
                async_set_remote_count(res)
            print("done f cloud")
        else:
            threading.Thread(target=signal_remote_scale_up, args=('f',)).start()
            print('running f local ', str(remoteCount))
            local.f()
            print('done f local')
    except Exception as e:
        print('Error running f:', e)
        error = True
    finally:
        return Response('cloud' if run_in_cloud else 'local', status=500 if error else 200)


@app.route('/g')
def g():
    run_in_cloud = cloud_has_warm_instance(GNAME)
    error = False
    try:
        if run_in_cloud:
            print('running g cloud', str(remoteCount))
            async_increment_remote_count(GNAME, -1)
            res = None
            try:
                res = get_request("/g")
            except:
                pass
                # local.g()
                # error = False
                # run_in_cloud = False
            if res:
                async_set_remote_count(res)
            print("done g cloud")
        else:
            threading.Thread(target=signal_remote_scale_up, args=('g',)).start()
            print('running g local', str(remoteCount))
            local.g()
            print("done g local")
    except Exception as e:
        print('Error running g', e)
        error = True
    finally:
        return Response('cloud' if run_in_cloud else 'local', status=500 if error else 200)



@app.route('/h')
def h():
    run_in_cloud = cloud_has_warm_instance(HNAME)
    error = False
    try:
        if run_in_cloud:
            print('running h cloud', str(remoteCount))
            async_increment_remote_count(HNAME, -1)
            res = None
            try:
                res = get_request("/h")
            except:
                pass
                # local.h()
                # error = False
                # run_in_cloud = False
            if res:
                async_set_remote_count(res)
            print("done h cloud")
        else:
            threading.Thread(target=signal_remote_scale_up, args=('h',)).start()
            print('running h local', str(remoteCount))
            local.h()
            print("done h local")
    except Exception as e:
        print('Error running h:', e)
        error = True
    finally:
        return Response('cloud' if run_in_cloud else 'local', status=500 if error else 200)


@app.route('/hb')
def hb():
    run_in_cloud = cloud_has_warm_instance(HBNAME)
    error = False
    try:
        if run_in_cloud:
            print('running hb cloud', str(remoteCount))
            async_increment_remote_count(HBNAME, -1)
            res = None
            try:
                res = get_request("/hb")
            except:
                pass
                # local.hb()
                # error = False
                # run_in_cloud = False
            if res:
                async_set_remote_count(res)
            print("done hb cloud")
        else:
            threading.Thread(target=signal_remote_scale_up, args=('hb',)).start()
            print('running hb local', str(remoteCount))
            local.hb()
            print("done hb local")
    except Exception as e:
        print('Error running hb:', e)
        error = True
    finally:
        return Response('cloud' if run_in_cloud else 'local', status=500 if error else 200)


if __name__ == '__main__':
    threading.Thread(target=update_remote_count).start()
    app.run()
