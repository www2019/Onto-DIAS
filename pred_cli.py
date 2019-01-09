import getopt,sys
from core.nlp_engine_cnn.pred import predict

# 获取命令行参数

try:
    options,args = getopt.getopt(sys.argv[1:],"i:",["input="])
    predict(x_raw=args)
    sys.exit()
except getopt.GetoptError:
    sys.exit()
