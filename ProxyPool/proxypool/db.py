import redis
from .settings import *
class Reids_client(object):
    def __init__(self):
        if PASSWORD:
            self._db = redis.Redis(host =HOST,port = PORT,password=PASSWORD)
        else:
            self._db = redis.Redis(host =HOST,port = PORT)
    #从头获取一定数量的代理，是为了校验
    def get(self,count=1):
        proxies = self._db.lrange(PROXIES,0,count-1)
        #删除，将获取到的代理删除。
        self._db.ltrim(PROXIES,count,-1)
        return proxies
    #提供一个从尾部获取代理的方法
    def pop(self):
        try:
            return self._db.rpop(PROXIES).decode('utf-8')
        except Exception:
            print('代理池为空！|无法获取！')
    def put(self,proxy):
        self._db.rpush(PROXIES,proxy)

    #获取代理池的长度
    @property
    def queue_len(self):
        return self._db.llen(PROXIES)

    #删除代理池
    def fulsh(self):
        self._db.flushdb()


