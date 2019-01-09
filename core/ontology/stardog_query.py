from urllib.parse import quote
import requests
import time
import random

from core.static.consts import DATASOURCE_YML_CONFIG_FILE
from core.static.consts import STARGOD_QUERY_GET_HEADERS
from core.static.consts import logger

sparql_query_config = DATASOURCE_YML_CONFIG_FILE["database"]["stardog"]


def get_query(spqrql,prefix):

    sparq_script = prefix + spqrql

    encoded = quote(sparq_script, 'utf-8')

    url = "http://"+sparql_query_config["host"]+":"+str(sparql_query_config["port"])+"/"+sparql_query_config["db"]+"/query?query="

    resp = requests.get(url=url+encoded, headers=STARGOD_QUERY_GET_HEADERS)

    if resp.status_code != 200:
        logger.error("Stardog http service got problem , status code :",resp.status_code)

    return resp.text
