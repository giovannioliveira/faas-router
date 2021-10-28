from flask import Flask, request
import local
import edge
import threading

app = Flask(__name__)


def cloud_has_warm_instance(function_name):
    return False


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello, Goodbye.'


@app.route('/f')
def f():
    if cloud_has_warm_instance('f'):
        print("make a call to cloud for f")
    else:
        return local.f()


@app.route('/g')
def g():
    if cloud_has_warm_instance('g'):
        print("make a call to cloud for g")
    else:
        return local.g()


@app.route('/h')
def h():
    x = int(request.args.get('x'))
    if cloud_has_warm_instance('h'):
        print("make a call to cloud for h")
    else:
        return str(local.h(x))


if __name__ == '__main__':
    threading.Thread(target=edge.simulate_arrival).start()
    app.run()
