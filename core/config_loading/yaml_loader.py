from yaml import load
import os


class YAMLLoader:

    def load_file(self, file_path, file_name):

        yaml = os.path.join(file_path, file_name)

        file = open(yaml)  # 打开yaml文件

        config = load(file)

        return config  # 使用load方法加载

