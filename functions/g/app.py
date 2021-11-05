import os
import time
from flask import Flask

app = Flask(__name__)


@app.route('/')
def f():
   t0 = time.time_ns()
   time.sleep(100)
   return str(time.time_ns() - t0)


if __name__ == "__main__":
   app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))