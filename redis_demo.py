# __author: Lambert
# __date: 2017/11/10 11:39
import redis

pool = redis.ConnectionPool(host='192.168.1.6', port=6379)
r = redis.Redis(connection_pool=pool)
r.set('foo', 'Bar111')
print(r.get('foo'))
