
from core.datasource.static import TYPE_DICT


class DFHandler:

    @classmethod
    def schema_reformat(cls,dataframe,col_type):

        # 此处不知道是否创建多个 df 浪费资源
        for col,type in col_type.items():
            dataframe = dataframe.withColumn(col,dataframe[col].cast(TYPE_DICT[type]))

        return dataframe
