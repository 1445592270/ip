from ProxyPool.proxypool.scheduler import Scheduler
from ProxyPool.proxypool.api import app
def main():
    s = Scheduler()
    s.run()
    app.run()
if __name__ == '__main__':
    main()
