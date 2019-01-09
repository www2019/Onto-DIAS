from pyspark.sql.functions import monotonically_increasing_id

'''

'''


class ViewProcessor:
    @classmethod
    def add_column_id(cls,dataframe):
        return dataframe.withColumn("id",monotonically_increasing_id())
