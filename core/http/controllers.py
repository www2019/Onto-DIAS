from flask import Flask,request

from core.social_media.facebook import webhook_msg_entry
from core.social_media.facebook import webhook_nlp_location_processing
from core.social_media.facebook import webhook_nlp_question_processing
from core.social_media.facebook import webhook_response_message
from core.social_media.facebook import webhook_nlp_datetime_processing
from core.social_media.facebook import webhook_attachment_location_processing
from core.static.consts import logger
from core.static.consts import redis_client


app = Flask(__name__)

import threading
locker = threading.Lock()
'''
    主API
'''

# facebook webhook
@app.route('/facebook/webhook', methods=['POST'])
def facebook_webhook_post():

    params = request.json

    print(params)

    locker.acquire()
    # 目前演示的都为取第0个  日后可能有问题
    if "entry" in params.keys():

        if "messaging" in params["entry"][0].keys():

            if 'read' in params["entry"][0]["messaging"][0].keys():

                if 'seq' in params["entry"][0]["messaging"][0]['read'].keys():

                    # 目前认为序列号为0的时候回执消息
                    if params["entry"][0]["messaging"][0]['read']['seq'] == 0:
                        return "EVENT_RECEIVED", 200

            if 'message' in params["entry"][0]["messaging"][0].keys():

                if 'is_echo' not in params["entry"][0]["messaging"][0]['message'].keys():

                    recipient_id = params["entry"][0]["messaging"][0]["sender"]["id"]

                    if "text" in params["entry"][0]["messaging"][0]["message"].keys():


                        # 分析nlp的结果
                        if 'nlp' not in params["entry"][0]["messaging"][0]['message'].keys():
                            logger.error("Can not solved the message because without nlp element.")

                            return "EVENT_RECEIVED", 200

                        # 获得文本
                        text = params["entry"][0]["messaging"][0]["message"]["text"]

                        redis_client.hset(recipient_id, "user_input_text",text)

                        # 首先判断是不是询问hazard并且是疑问句
                        tag = webhook_nlp_question_processing(recipient_id,params["entry"][0]["messaging"][0]['message']['nlp'])

                        if redis_client.hget(recipient_id,"hazard_chat_status") is None:
                            if tag is None or tag != 1:
                                if 'entities' in params["entry"][0]["messaging"][0]['message']['nlp'].keys():
                                    # 强制是判断时间或者位置的消息
                                    if 'datetime' not in params["entry"][0]["messaging"][0]['message']['nlp']['entities'].keys() \
                                            and 'location' not in params["entry"][0]["messaging"][0]['message']['nlp']['entities'].keys():
                                        if 'greetings' in params["entry"][0]["messaging"][0]['message']['nlp']['entities'].keys():
                                            if len(params["entry"][0]["messaging"][0]['message']['nlp']['entities']['greetings']) >0:
                                                if 'confidence' in params["entry"][0]["messaging"][0]['message']['nlp']['entities']['greetings'][0]:
                                                    # 目前定0.989 以上为一定是打招呼 , 目前小于0.989 证明输入错误
                                                    if params["entry"][0]["messaging"][0]['message']['nlp']['entities']['greetings'][0]['confidence'] < 0.989:
                                                        response = "I can not understand this now, sorry !"
                                                        webhook_response_message(recipient_id, response)
                                        response = "I can answer question in Landslip domain, and you can ask me some questions like:"
                                        response += "\n\t 1. I saw leanning pole, what kinds of hazard will happen ?"
                                        response += "\n\t 2. The leanning pole happened in London, which hazards will happen ?"
                                        response += "\n\t 3. The New York was happend telephone leaning pole from 03/03/2010 to 21/03/2010, which hazards will happen ?"
                                        webhook_response_message(recipient_id, response)
                            locker.release()
                            return "EVENT_RECEIVED",200

                        # ontology 检索
                        webhook_msg_entry(recipient_id, text)

                        # 取时间
                        webhook_nlp_datetime_processing(recipient_id,params["entry"][0]["messaging"][0]['message']['nlp'])

                        # 取地理位置信息
                        webhook_nlp_location_processing(recipient_id,params)

                        webhook_msg_entry(recipient_id, text)

                    if 'attachments' in params["entry"][0]["messaging"][0]['message'].keys() and \
                        redis_client.hget(recipient_id,"hazard_chat_status") == "start":
                        # 取地理位置信息
                        webhook_attachment_location_processing(recipient_id, params)
                        webhook_msg_entry(recipient_id, redis_client.hget(recipient_id, "user_input_text"))

                    if redis_client.hget(recipient_id, "hazard_chat_status") is not None:
                        if redis_client.hget(recipient_id, "hazard_chat_status") == "end":
                            redis_client.hdel(recipient_id, "hazard_chat_status")
                            redis_client.hdel(recipient_id, "question_seq")
                            redis_client.hdel(recipient_id, "date")
                            redis_client.hdel(recipient_id, "location")
                            redis_client.hdel(recipient_id, "ontology_result_hazards")

    locker.release()
    return "EVENT_RECEIVED",200

@app.route('/facebook/webhook', methods=['GET'])
def facebook_webhook_get():

    challenge = request.args.get("hub.challenge")

    return challenge,200

def http():
    app.debug = True
    app.run(host='0.0.0.0',port=8089,ssl_context=('/home/ubuntu/CA/1701986_www.raytesting.cn.pem', '/home/ubuntu/CA/1701986_www.raytesting.cn.key'))

