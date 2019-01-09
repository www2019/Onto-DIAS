

'''
    mysql data source
'''


class MysqlDataSource:

    @classmethod
    def get_table_dataframe(cls,spark_session,database,table,view_name,addr="localhost",port="3306",username="root",password="Root@2018"):

        # 创建mysql dataframe
        mysql_df = spark_session.read.format("jdbc").option("url", "jdbc:mysql://"+addr+":"+port+"/"+database)\
            .option("driver","com.mysql.jdbc.Driver").option("dbtable", table)\
            .option("user", username)\
            .option("password", password).load()

        # 创建view
        mysql_df.createOrReplaceTempView(view_name)

        return mysql_df
