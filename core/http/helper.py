'''
    HDFS 备用包
    from hdfs3 import HDFileSystem
    这个包需要安装依赖  参考：
    https://hdfs3.readthedocs.io/en/latest/install.html
'''

import os
import json
from urllib.parse import unquote
from urllib import parse
from pyhdfs import HdfsClient


from core.datasource.tif_file import transform_raster_to_array
from core.datasource.tif_file import create_raster_from_array
from core.nlp_engine_cnn.pred import predict
from core.data_analysis.analysis import Analysiser
from core.static.consts import redis_client
from core.ontology.stardog_helper import metadata_query_hazards


from core.static.consts import ONTOLOGY_YML_CONFIG_FILE

def location_processing(recipient_id,location):

    if location["type"] != "location":
        response = "Can not get your location, please try again."
        return response

    title = location["title"]
    url = location["url"]
    coordinates_lat = location["payload"]["coordinates"]["lat"]
    coordinates_long = location["payload"]["coordinates"]["long"]

    location_url = unquote(url, encoding='utf-8', errors='replace')

    # 提炼出地图url中具体地址信息
    params = parse.urlparse(location_url)
    params_dic = parse.parse_qs(params.query)
    address = ""

    for i in params_dic["where1"]:
        address = address + i + ","

    location["address_detail"]=address


    return location

def searching_req_ask(recipient_id,msg):

    '''
        此处需要分析用户输入的内容
    '''

    # 分类预测 并且发送ontology查询
    pred_result, ontology_result = predict(msg)

    # all_result = [pred_result, ontology_result]

    text = "The hazard :"

    if "LeaningTelephonePole" not in ontology_result.keys():
        return "No ontology result !"

    for val in ontology_result["LeaningTelephonePole"]:
        text = text + val + ", "


    # 存入hazard结果  这里只处理了leaningpole
    redis_client.hset(recipient_id,"ontology_result_hazards",json.dumps(ontology_result["LeaningTelephonePole"]))

    text = text + "probably happen."

    return text


def searching_resp_time_location(recipient_id):
    response = []

    # 这里需要查找metadata  然后找到关联的数据  然后根据时间条件或者其他条件进行筛选
    data = redis_client.hget(recipient_id, "ontology_result_hazards")
    hazards = json.loads(data)
    metadata_raw = metadata_query_hazards(hazards,ONTOLOGY_YML_CONFIG_FILE['prefix']['query']['by_warning_sign'])

    # if metadata_raw is not None:
    #     print(metadata_raw)

    response.append("# Suggestion from knowledge base: \n\tAccording to a system analysis, there is a chance for the occurrence of  "+hazards[0])

    # 此处需要匹配地理位置

    date = redis_client.hget(recipient_id,"date")
    if date is None:
        return None

    dict = json.loads(date)

    if dict["type"] != "interval":
        response = ["Now system only support period of date, sorry."]
        return response

    date = [dict["from"], dict["to"]]

    res = Analysiser.get_avg(date)

    text = "# Statistical Processing : \n\tMore details, average value of every related data as follow :\n"
    text = text + "\t 1. BGS_north_slope_lower [" + "Temp1C :" + str(res["l_avg"]["Temp1C"]) + ", \n\t\t" \
               + "Temp2C :" + str(res["l_avg"]["Temp2C"]) + ", \n\t\t" \
               + "Potential1kPa :" + str(res["l_avg"]["Potential1kPa"]) + ", \n\t\t" \
               + "Potential2kPa :" + str(res["l_avg"]["Potential2kPa"]) + "] "

    response.append(text + "\n\t 2. BGS_north_slope_higher [" + "Temp1C :" + str(res["h_avg"]["Temp1C"]) + ", \n\t\t" \
               + "Temp2C :" + str(res["h_avg"]["Temp2C"]) + ", \n\t\t" \
               + "Potential1kPa :" + str(res["h_avg"]["Potential1kPa"]) + ", \n\t\t" \
               + "Potential2kPa :" + str(res["h_avg"]["Potential2kPa"]) + "] ")

    # tif 测试

    rasterOrigin = (-123.25745, 45.43013)
    pixelWidth = 10
    pixelHeight = 10
    newRasterfn = 'result.tif'
    newRasterfn_path = './maps/result.tif'

    hdfs = HdfsClient(hosts="ip-172-31-16-144,50000")
    hdfs.copy_to_local('/data/map/demo/input1.tif', './maps/input1.tif')
    hdfs.copy_to_local('/data/map/demo/input2.tif', './maps/input2.tif')
    hdfs.copy_to_local('/data/map/demo/input1.tif', '/var/www/html/landslip/input1.tif')
    hdfs.copy_to_local('/data/map/demo/input2.tif', '/var/www/html/landslip/input2.tif')

    tif1 = "./maps/input1.tif"
    tif2 = "./maps/input2.tif"

    tif1_arr = transform_raster_to_array(tif1)
    tif2_arr = transform_raster_to_array(tif2)

    test_arr = tif1_arr + tif2_arr

    create_raster_from_array(newRasterfn_path, rasterOrigin, pixelWidth, pixelHeight, test_arr)

    # 此处需要检查 是否存在目标文件
    hdfs.delete("/data/map/demo/"+newRasterfn)
    hdfs.copy_from_local("./maps/"+newRasterfn, '/data/map/demo/'+newRasterfn)
    hdfs.copy_to_local('/data/map/demo/'+newRasterfn, '/var/www/html/landslip/'+newRasterfn)


    os.remove(os.path.join("./maps", "input1.tif"))
    os.remove(os.path.join("./maps", "input2.tif"))
    os.remove(newRasterfn_path)

    # 地址可能需要改为https
    response.append("\n # Geo-spatial Processing: \n\tThe .tif file results directory download link:  " + "\n\t http://18.130.118.154/landslip/")

    return response

