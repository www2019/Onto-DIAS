
'''
    hdfs data frame
'''


class HDFSDataSource:

    @classmethod
    def get_file_dataframe(cls,spark_session,namenode,port,path,file_type,view_name,col=None):

        file = "hdfs://"+namenode+":"+str(port)+path

        # 使用spark 读 csv
        # 从文件中加载头信息
        # 自动推导 schema
        hdfs_df = spark_session.read.format(file_type).option("header", "true").option("inferSchema", "true").load(file)

        hdfs_df.createOrReplaceTempView(view_name)

        return hdfs_df




