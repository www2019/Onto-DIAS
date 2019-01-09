

'''
    mongodb data source
'''


class MongoDBDataSource:

    @classmethod
    def get_collection_dataframe(cls,spark_session,database,collection,view_name,addr="localhost",port="27017",username="root",password="Root@2018"):

        # 创建mongodb dataframe
        mongodb_df = spark_session.read.format("com.mongodb.spark.sql.DefaultSource")\
            .option("spark.mongodb.input.uri","mongodb://"+addr+"/"+database+"."+collection+"")\
            .option("spark.mongodb.output.uri", "mongodb://"+addr+"/"+database+"."+collection+"").load()

        # 创建view
        mongodb_df.createOrReplaceTempView(view_name)

        return mongodb_df
