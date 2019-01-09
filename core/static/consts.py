from core.config_loading.yaml_loader import YAMLLoader
from core.log_management.logger import Logger
import redis

# datasource_config.yaml
DATASOURCE_YML_CONFIG_FILE = YAMLLoader.load_file("", file_path="./conf", file_name="datasource_config.yaml")

# cnn_config.yaml
CNN_YML_CONFIG_FILE = YAMLLoader.load_file("", file_path="./conf", file_name="cnn_config.yaml")

# ontology_config.yaml
ONTOLOGY_YML_CONFIG_FILE = YAMLLoader.load_file("", file_path="./conf", file_name="ontology_config.yaml")

# ontology_config.yaml
SYSTEM_CONFIG_FILE = YAMLLoader.load_file("", file_path="./conf", file_name="sys_config.yaml")

STARGOD_QUERY_GET_HEADERS = headers = {
        'Content-Type': 'application/x-www-form-urlencoded, application/sparql-query',
        'Accept': 'text/turtle, application/rdf+xml, application/n-triples, application/trig,'
                  ' application/n-quads, text/n3, application/trix, application/ld+json,'
                  ' application/sparql-results+xml,'
                  ' application/sparql-results+json, application/x-binary-rdf-results-table, text/boolean, text/csv,'
                  ' text/tsv, text/tab-separated-values'
    }

logger = Logger()

VERIFY_TOKEN = "EAAiUqbKxWqoBAEHXuEjODFIQBn407x6ctuS9lItZCiYYMUnjSEWZCySy7iQDoYLVrJvzzZBS6hIE3ZChv8NNZCkWGfzNQCWqcN0Uf5J3gywfQ08NxJUCyfesywU6oNPhpFF56K9RAZCZBoHVZB5lIwfWEzCPN1AhDUenT6UmaKxlTgZDZD"

#创建连接池
pool = redis.ConnectionPool(host=SYSTEM_CONFIG_FILE["redis"]["host"],port=SYSTEM_CONFIG_FILE["redis"]["port"],decode_responses=True)

#创建链接对象
redis_client = redis.Redis(connection_pool=pool)