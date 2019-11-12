
#如果为空，就是没密码
PASSWORD = ''
HOST ='localhost'
PORT ='6379'

#代理池的名称
PROXIES = 'proxies'
#用百度来测试代理是否可用
TEST_API = 'https://www.baidu.com/'
#设置测试代理时长
PROXY_TEST_TIME_OUT = 10

#代理池最少代理数量
POOL_LOWER_THRESHOLD = 30
#代理池最大代理数量
POOL_UPPER_THRESHOLD = 100
#代理池循环检查添加代理时间
POOL_CYCLE_CHECK_TIME = 10
#代理池循环校验时间
VLLID_CHECK_CYCLE_TIME = 10