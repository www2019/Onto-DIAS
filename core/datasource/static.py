from pyspark.sql.types import *


'''
    所有类型的对应的字典
'''
TYPE_DICT = {
    1: DateType(),
    2: IntegerType(),
    3: FloatType(),
    4: StringType()
}