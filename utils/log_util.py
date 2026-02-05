import logging
import os
import time
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class Logger:
    """
    封装logger并添加handler：
        console_handler：%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s
        file_handler:%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s
    最后用get_logger()安全返回logger对象
    """
    def __init__(self):
        self.logger = logging.getLogger('MiniShopLogger')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(console_formatter)
            console_handler.setLevel(logging.INFO)

            log_path = os.path.join(BASE_DIR, 'logs')
            if not os.path.exists(log_path):
                os.makedirs(log_path)
            file_formatter = logging.Formatter('%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s')
            log_full_path = os.path.join(BASE_DIR, 'logs',f'{time.strftime("%Y-%m-%d", time.localtime())}.log')
            file_handler = logging.FileHandler(log_full_path, encoding='utf-8')
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(logging.DEBUG)

            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger

logger = Logger().get_logger() #实例化，之后其他文件调用的都是这个logger，防止创建多个不同logger浪费资源




