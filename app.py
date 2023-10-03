from flask import Flask, request, make_response
import redis
import time
import os


app = Flask(__name__)

subnet_mask = os.environ.get('MASK','24')
limit = int(os.environ.get('LIMIT',2))
wait_time = int(os.environ.get('WAIT_TIME',10))
redis_connect = redis.Redis(host='redis', port=6379, db=0)

def check_rate_limit(request_count):
    if request_count > limit:
        response = make_response('Rate limit exceeded', 429)
        reset_time = int(time.time()) + wait_time
        response.headers['Retry-After'] = str(reset_time)
        return response
    return 'Hello, world!'

@app.route('/')
def index():
    client_ip = '.'.join(request.remote_addr.split('.')[:-1]) + '.*'
    key = f'request_limit: {client_ip}/{subnet_mask}'
    request_count = redis_connect.get(key)
    if request_count is None:
        redis_connect.setex(key, wait_time, 1)
        request_count = 1
    else:
        redis_connect.incr(key)
        request_count = int(request_count) + 1

    return check_rate_limit(request_count)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
