# -*- coding: UTF-8 -*-
# 从cninfo拉取所有股票至今的全部日K数据
import time
import json
from qcinfo.log import task_log
import traceback
from qcinfo import cninfo
from qcinfo import qcrepo

logger = task_log()

stocks = qcrepo.stocks()
count = 0
for index, row in stocks.iterrows():
    try:
        code = row["seccode"]
        quotes = cninfo.daily_line(code)
        # 判断最后一条行情数据的日期是否和今天相等，来判断cninfo的数据是否有缺失
        times = quotes[-1][0]
        date = time.strftime("%Y-%m-%d", time.localtime(times / 1000))
        if date != "2019-06-13":
            logger.info("code: " + code + " last timestamp is: " + date + " not today, need to retry!")
        qcrepo.set_quotes(code, "d", json.dumps(quotes))
        count += 1
        logger.info(str(count) + " fetch " + str(code) + " success.")
        time.sleep(2)   # 防止太快 被封
    except:
        logger.error(traceback.format_exc())
        continue