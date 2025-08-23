import logging
import os
from logging.handlers import RotatingFileHandler

logfile = os.path.join('log', 'app.log')
#ログのローテーション設定
handler = RotatingFileHandler(
    logfile, #ログファイル名
    maxBytes=1024 * 1024, #1MBごとにローテーション
    backupCount=3, #バックアップファイルの数
    encoding='utf-8'  # ログファイルのエンコーディング
)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

