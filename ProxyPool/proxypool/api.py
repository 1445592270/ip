from flask import Flask,g

from .db import Reids_client

__all__=['app']
app = Flask(__name__)

def get_conn():
    if not hasattr(g,'redis_client'):
        g.redis_client = Reids_client()
    return g.redis_client
@app.route('/')
def index():
    return '<h1>欢迎来打0715代理池！<h1>'
@app.route('/get')
def get():
    try:
        conn = get_conn()
        return conn.pop()
    except Exception:
        return '<h1>代理池还没数据！<h1>'
@app.route('/count')
def count():
    conn = get_conn()
    return conn.queue_len
