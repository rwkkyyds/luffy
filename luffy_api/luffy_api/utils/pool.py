

import redis
POOL=redis.ConnectionPool(max_connections=10,host="localhost",port=6379)