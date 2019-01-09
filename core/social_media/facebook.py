import requests
import json

from core.http.helper import searching_req_ask
from core.http.helper import searching_resp_time_location
from core.http.helper import location_processing
from core.static.consts import VERIFY_TOKEN
from core.static.consts import redis_client
from core.redis_manager.operation import add_value_location

def webhook_msg_entry(recipient_id,text):

    question_seq = redis_client.hget(recipient_id, "question_seq")

    if question_seq is None:
        return

    #
    if question_seq == "1":

        all_text = []
        all_text.append(text)

        res = searching_req_ask(recipient_id,all_text)

        webhook_response_message(recipient_id,res)

        # 第一个问题回答完成
        redis_client.hset(recipient_id, "question_seq", "2")
    elif question_seq == "2" and \
        redis_client.hget(recipient_id, "date") is not None and\
        redis_client.hget(recipient_id, "location") is not None:

        res = searching_resp_time_location(recipient_id)
        if res is not None:
            if len(res) != 0:
                for resp in res:
                    webhook_response_message(recipient_id,resp)
                # 意味着hazard对话已经结束
                redis_client.hset(recipient_id, "hazard_chat_status", "end")

                # 结束问题
                redis_client.hset(recipient_id, "question_seq", "0")

def webhook_response_message(recipient_id,resp_text):

    data = {"messaging_type": "RESPONSE",
                "recipient":{
                "id":recipient_id
            },
            "message":{
            "text":resp_text
            }
            }

    headers = {
        'Content-Type': 'application/json'
    }

    addr = "https://graph.facebook.com/v2.6/me/messages?access_token="
    resp = requests.post(
        addr+VERIFY_TOKEN, data=json.dumps(data), headers=headers)

    print(resp.text)


def webhook_nlp_location_processing(recipient_id,params):

    nlp = params["entry"][0]["messaging"][0]['message']['nlp']

    if 'entities' not in nlp.keys():
        return

    if redis_client.hget(recipient_id,"hazard_chat_status") is None:
        return
    elif redis_client.hget(recipient_id,"hazard_chat_status") == "end":
        return

    if 'location' not in nlp["entities"].keys() and \
        redis_client.hget(recipient_id,"hazard_chat_status") == "start":
        check_element_location(recipient_id)
        return
        # 只要开始了对话就必须先提供时间日期


    # 不止一个地区结果
    # 目前默认为1个地区结果
    if len(nlp["entities"]['location']) != 1:
        response = "This system is not support multi-location."
        webhook_response_message(recipient_id, response)
        return

    response = ""
    if 'resolved' not in nlp["entities"]['location'][0]:

        # 可以拿到准确的位置信息
        if 'suggested' in nlp["entities"]['location'][0].keys():

            if nlp["entities"]['location'][0]['suggested']:

                location = nlp["entities"]['location'][0]['value']

                add_value_location(recipient_id,location)

                response = "Got the location : "+location

    elif len(nlp["entities"]['location'][0]['resolved']['values']) != 1:

        # 详细信息可以用下面的进一步取
        all_prob_location = ""

        for val in nlp["entities"]['location'][0]['resolved']['values']:
            if 'external' in val.keys():
                if 'wikipedia' in val['external'].keys():
                    all_prob_location = all_prob_location + "\n\t" + val['external']['wikipedia']
                else:
                    all_prob_location = all_prob_location + "\n\t" + val['name']

        location = nlp["entities"]['location'][0]["value"]
        add_value_location(recipient_id, location)
        response = "Got the location : " + location
        webhook_response_message(recipient_id, response)
        response = "\nAll relative location bask on your mentioned "+ nlp["entities"]['location'][0]['value'] + " you can input the full name next time."+all_prob_location


    webhook_response_message(recipient_id,response)


def webhook_nlp_datetime_processing(recipient_id,nlp):

    if 'entities' not in nlp.keys():
        return

    if redis_client.hget(recipient_id,"hazard_chat_status") is None:
        return
    elif redis_client.hget(recipient_id,"hazard_chat_status") == "end":
        return

    # 只要开始了对话就必须先提供时间日期
    if 'datetime' not in nlp["entities"].keys() and \
        redis_client.hget(recipient_id,"hazard_chat_status") == "start":
        check_element_date(recipient_id)
        return

    # 目前只支持一个datetime
    # if len(nlp["entities"]["datetime"]) > 1:
    #     response = "How only suport one datatime in one message."
    #     webhook_response_message(recipient_id, response)
    #     return

    # 判断类型
    if 'type' in nlp["entities"]["datetime"][0]:

        response = ""

        # 指定日期以及 今天明天昨天关键词
        if nlp["entities"]["datetime"][0]["type"] == "value":

            if 'value' in nlp["entities"]["datetime"][0]:

                date = nlp["entities"]["datetime"][0]['value'].split('T')[0]

                if not redis_client.hexists(recipient_id,"date"):

                    # 如果已经已经有的话更新,没有就创建
                    redis_client.hset(recipient_id,"date",json.dumps({"value":date,"type":"value"}))
                else:
                    info = redis_client.hget(recipient_id,"date")

                    dict = json.loads(info)

                    # 直接更新data
                    dict['value'] = date
                    dict['type'] = "value"

                    redis_client.hset(recipient_id,"date",json.dumps(dict))

                    response = "Got the date : " + date


        # 一段时间 目前只支持输入 from 。。。  to ...
        if nlp["entities"]["datetime"][0]["type"] == "interval":

            if 'from' in nlp["entities"]["datetime"][0] and 'to' in nlp["entities"]["datetime"][0]:

                # 当前只取date
                date_from = nlp["entities"]["datetime"][0]["from"]["value"].split('T')[0]

                date_to = nlp["entities"]["datetime"][0]["to"]["value"].split('T')[0]

                if not redis_client.hexists(recipient_id, "date"):

                    # 如果已经已经有的话更新,没有就创建
                    redis_client.hset(recipient_id,"date",json.dumps({"from":date_from,"to":date_to,"type":"interval"}))
                else:
                    info = redis_client.hget(recipient_id,"date")

                    dict = json.loads(info)

                    # 直接更新data
                    dict['from'] = date_from
                    dict['to'] = date_to
                    dict['type'] = "interval"

                    redis_client.hset(recipient_id,"date", json.dumps(dict))

                    response = "Got the period of date : from " + date_from +" to "+date_to

        webhook_response_message(recipient_id, response)


def webhook_nlp_question_processing(recipient_id,nlp):

    '''
        return:
            0 表示没有疑问词 what which
            1 表示成功
            2 表示没有hazard 关键词
    '''

    if 'entities' not in nlp.keys():
        return None

    if 'question_keyword' not in nlp["entities"].keys():
        return 0

    keyword_tag = False

    for keyword in nlp["entities"]['question_keyword']:
        if keyword['value'] == "what" or keyword['value'] == "which":
            keyword_tag = True

    if not keyword_tag:
        return 0

    if 'hazard_keyword' not in nlp["entities"].keys():
        return 2

    # 意味着hazard对话已经开始
    redis_client.hset(recipient_id,"hazard_chat_status","start")
    redis_client.hset(recipient_id, "question_seq", "1")

    return 1

def webhook_attachment_location_processing(recipient_id,params):

    if redis_client.hget(recipient_id,"hazard_chat_status") is None:
        return
    elif redis_client.hget(recipient_id,"hazard_chat_status") == "end":
        return

    # 判断是否发送的是位置附件app
    elif 'attachments' in params["entry"][0]["messaging"][0]['message'].keys():

        info = location_processing(recipient_id,params["entry"][0]["messaging"][0]['message']['attachments'][0])
        if info is not None:

            if type(info) == "string":
                webhook_response_message(recipient_id, info)
                return

            add_value_location(recipient_id,info["title"])

            response = "Got the location : " + info["title"] +\
                       "\nAddress: "+info['address_detail']

            webhook_response_message(recipient_id, response)

            # 检查一下时间
            check_element_date(recipient_id)

            return

def check_element_date(recipient_id):
    if redis_client.hget(recipient_id, "date") is None:
        response = "Could you tell me about the date or period of date ?"
        webhook_response_message(recipient_id, response)
    return


def check_element_location(recipient_id):
    if redis_client.hget(recipient_id, "location") is None:
        response = "Could you tell me the location ?"
        webhook_response_message(recipient_id, response)
    return
