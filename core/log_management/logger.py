import logging
import logging.handlers
import os,time

'''
    logger显示管理用途
    目前文件输出有问题： 只会覆盖不会追加
'''

# 定义日志输出格式 结束

BASE_LOG_DIR = "./logs/" # log文件的目录

# 如果不存在定义的日志目录就创建一个
if not os.path.isdir(BASE_LOG_DIR):
    os.mkdir(BASE_LOG_DIR)

# log文件的全路径
log_filename = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime()) + ".log"

#logging_config.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'logfile_path': BASE_LOG_DIR,
    'filemode': 'w',
    'datefmt': '%a, %d %b %Y %H:%M:%S',
    'formatters': {
        'standard': {
            'format': '[%(asctime)s][%(threadName)s:%(thread)d][task_id:%(name)s][%(filename)s:%(lineno)d]'
                      '[%(levelname)s][%(message)s]'
        },
        'simple': {
            'format': '[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]%(message)s'
        },
        'collect': {
            'format': '%(message)s'
        }
    },
    'handlers': {
        #打印到终端的日志
        'console': {
            'level': logging.DEBUG,
            'filters': ['require_debug_true'],
            'class': logging.StreamHandler,
            'formatter': '[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]%(message)s'
        },
        #打印到文件的日志,收集info及以上的日志
        'default': {
            'level': logging.INFO,
            'class': logging.handlers.RotatingFileHandler,  # 保存到文件，自动切
            'filename': log_filename,  # 日志文件
            'maxBytes': 1024 * 1024 * 5,  # 日志大小 5M
            'backupCount': 3,
            'formatter': '[%(asctime)s][%(threadName)s:%(thread)d][task_id:%(name)s][%(filename)s:%(lineno)d]'
                      '[%(levelname)s][%(message)s]',
            'encoding': 'utf-8',
        },
        #打印到文件的日志:收集错误及以上的日志
        'error': {
            'level': logging.ERROR,
            'class': logging.handlers.RotatingFileHandler,  # 保存到文件，自动切
            'filename': log_filename,  # 日志文件
            'maxBytes': 1024 * 1024 * 5,  # 日志大小 5M
            'backupCount': 5,
            'formatter': '[%(asctime)s][%(threadName)s:%(thread)d][task_id:%(name)s][%(filename)s:%(lineno)d]'
                      '[%(levelname)s][%(message)s]',
            'encoding': 'utf-8',
        },
        #打印到文件的日志
        'collect': {
            'level': logging.INFO,
            'class': logging.handlers.RotatingFileHandler,  # 保存到文件，自动切
            'filename': log_filename,
            'maxBytes': 1024 * 1024 * 5,  # 日志大小 5M
            'backupCount': 5,
            'formatter': '%(message)s',
            'encoding': "utf-8"
        }
    },
    'loggers': {
        #logging.getLogger(__name__)拿到的logger配置
        '': {
            'handlers': ['default', 'console', 'error'],
            'level': 'DEBUG',
            'propagate': True,
        },
        #logging.getLogger('collect')拿到的logger配置
        'collect': {
            'handlers': ['console', 'collect'],
            'level': 'INFO',
        }
    },
}


class Logger(object):

    def __init__(self):

        logging.basicConfig(
            level= LOGGING["handlers"]["default"]["level"],
            format= LOGGING["formatters"]["standard"]["format"],
            datefmt= LOGGING["datefmt"],
            filename= LOGGING["logfile_path"]+LOGGING["handlers"]["default"]["filename"],
            filemode= LOGGING["filemode"]
        )

        handler = logging.handlers.RotatingFileHandler(LOGGING["logfile_path"]+LOGGING["handlers"]["default"]["filename"]
                                                       , maxBytes=LOGGING["handlers"]["default"]["maxBytes"]
                                                       , backupCount=LOGGING["handlers"]["default"]["backupCount"]
                                                       , encoding=LOGGING["handlers"]["default"]["encoding"])

        logging.getLogger().addHandler(handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(LOGGING["handlers"]["default"]["level"])
        formatter = logging.Formatter(LOGGING["handlers"]["console"]["formatter"])
        console_handler.setFormatter(formatter)
        console_handler.filter(LOGGING["handlers"]["console"]["filters"])
        logging.getLogger().addHandler(console_handler)

    def info(self, msg):
        logging.info(msg)

    def warning(self, msg):
        logging.warning(msg)

    def debug(self, msg):
        logging.debug(msg)

    def critical(self, msg):
        logging.critical(msg)

    def error(self, msg):
        logging.error(msg)
