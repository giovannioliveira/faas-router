import os
import time
from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def f():
   if request.args.get('wakeup'):
      return 'ready'
   t0 = time.time_ns()
   time.sleep(10)
   return str(time.time_ns() - t0)


if __name__ == "__main__":
   app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
