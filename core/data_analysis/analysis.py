from core.datasource.hdfs import HDFSDataSource
from core.datasource.mysql import MysqlDataSource
from core.datasource.mongodb import MongoDBDataSource
from core.datasource.df_handler import DFHandler
from core.static.consts import DATASOURCE_YML_CONFIG_FILE
from core.static.consts import logger

from pyspark.sql import SparkSession

hdfs_config = DATASOURCE_YML_CONFIG_FILE["database"]

class Analysiser:
    @classmethod
    def get_avg(cls,filter):

        # 此处获取的参数用于 demo  气压

        # 创建dataframe
        spark = SparkSession \
            .builder \
            .appName("DAS_APP") \
            .getOrCreate()

        mysql_df = MysqlDataSource.get_table_dataframe(database="BGS",spark_session=spark,table="NorthSlopLowerRawData"
                                                       ,view_name="BGS_north_slope_lower_raw_data")

        # 读中部数据 nosql

        mongodb_df = MongoDBDataSource.get_collection_dataframe(spark_session=spark,database="BGS",
                                                                collection="BGS-north-slope-middle_raw_data",
                                                                view_name="BGS_north_slope_middle_raw_data")

        col_type ={
            "MeasurementTime": 1,
            "Day": 2,
            "Hour": 2,
            "Minute": 2,
            "m_slashm_1VWC": 3,
            "Temp1C": 3,
            "m_slashm_2VWC": 3,
            "Temp2C": 3,
            "Potential2kPa": 3,
            "Potential1kPa": 3
        }

        # 读低处数据
        hdfs_df = HDFSDataSource.get_file_dataframe(
            spark_session=spark,
            namenode=hdfs_config["hdfs"]["namenode"],
            port=hdfs_config["hdfs"]["port"],
            path="/data/BGS-north-slope-higher_raw_data.csv",
            file_type="csv",
            view_name="BGS_north_slope_higher_raw_data",
            col=col_type)


        # 查询 lower
        sql_str = "SELECT Temp1C,Temp2C,Potential1kPa,Potential2kPa FROM BGS_north_slope_lower_raw_data WHERE MeasurementTime BETWEEN '" +filter[0] + "' AND '" + filter[1] +"'"

        # 先查出来区间 然后取最大值
        sql = spark.sql(sql_str)

        col_type ={
            "Temp1C": 3,
            "Temp2C": 3,
            "Potential2kPa": 3,
            "Potential1kPa": 3
        }

        mysql_sql_df = DFHandler.schema_reformat(dataframe=sql,col_type=col_type)

        l_avg = mysql_sql_df.groupBy().avg("Temp1C","Temp2C","Potential1kPa","Potential2kPa").collect()


        # 查询 middle
        sql_str = "SELECT PotentialkPa FROM BGS_north_slope_middle_raw_data WHERE MeasurementTime BETWEEN '" +filter[0] + "' AND '" + filter[1] +"'"

        sql = spark.sql(sql_str)

        # 查询 higher
        sql_str = "SELECT Temp1C,Temp2C,Potential1kPa,Potential2kPa FROM BGS_north_slope_higher_raw_data WHERE MeasurementTime BETWEEN '" + \
                  filter[0] + "' AND '" + filter[1] + "'"

        sql = spark.sql(sql_str)


        col_type = {
            "Temp1C": 3,
            "Temp2C": 3,
            "Potential2kPa": 3,
            "Potential1kPa": 3
        }

        hdfs_sql_df = DFHandler.schema_reformat(dataframe=sql, col_type=col_type)

        h_avg = hdfs_sql_df.groupBy().avg("Temp1C", "Temp2C", "Potential1kPa", "Potential2kPa").collect()

        spark.stop()

        res = {
            "l_avg":{
                "Temp1C": l_avg[0][0],
                "Temp2C": l_avg[0][1],
                "Potential1kPa": l_avg[0][2],
                "Potential2kPa": l_avg[0][3]
            },

            "h_avg": {
                "Temp1C": h_avg[0][0],
                "Temp2C": h_avg[0][1],
                "Potential1kPa": h_avg[0][2],
                "Potential2kPa": h_avg[0][3]
            }
        }
        return res
