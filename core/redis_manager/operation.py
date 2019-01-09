import json
from core.static.consts import redis_client

def add_value_location(recipient_id,location):
    if not redis_client.hexists(recipient_id, "location"):

        # 如果已经已经有的话更新,没有就创建
        redis_client.hset(recipient_id, "location", json.dumps({"title": location}))
    else:
        info = redis_client.hget(recipient_id, "location")

        dict = json.loads(info)

        # 直接更新data
        dict['title'] = location

        redis_client.hset(recipient_id, "location", json.dumps(dict))


