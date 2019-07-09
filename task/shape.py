# -*- coding: UTF-8 -*-
# Stock hammer shape judge.
from basic import log
logger = log.Log()

def is_hammer_shape(quotes):
    # 趋势 跌
    trendb = trend_before(quotes)
    if trendb > 0:
        return False
    # 成交量趋势 跌
    val_trend = trend_before(quotes, item='volume')
    if val_trend > 0:
        return False

    q = quotes[-1]
    color = 1
    line = q['high'] - q['low']     # 线高
    entity = q['close'] - q['open'] # 实体高度
    top_h = q['high'] - q['close']    # 头高度
    footer = line - (q['high'] - q['open'])  # 脚高度
    if q['open'] > q['close']:
        color = -1
        entity = q['open'] - q['close']
        top_h = q['high'] - q['open']
        footer = line - (q['high'] - q['close'])

    # 十字或者一字板
    if q['open'] == q['close']:
        return False

    # 头部长度不超过10%
    if top_h > line * 0.1:
        return False

    # 实体长度不超过40%
    if entity > line * 0.3:
        return False

    # 分数
    score = round((footer / q['low']) * 1000, 2)
    if score < 15:
        return False

    return {
        'trend_before': trendb,
        'color': color,
        'score': score,
    }

def venus_shape_judge(quotes_list):
    q1 = quotes_list[-1]
    q2 = quotes_list[-2]
    q3 = quotes_list[-3]
    if q1['open'] > q1['close']:
        q1_h = q1['open']
        q1_l = q1['close']
        q1_t = -1
    else:
        q1_h = q1['close']
        q1_l = q1['open']
        q1_t = 1

    if q2['open'] > q2['close']:
        q2_h = q2['open']
        q2_l = q2['close']
        q2_t = -1
    else:
        q2_h = q2['close']
        q2_l = q2['open']
        q2_t = 1

    if q3['open'] > q3['close']:
        q3_h = q3['open']
        q3_l = q3['close']
        q3_t = -1
    else:
        q3_h = q3['close']
        q3_l = q3['open']
        q3_t = 1

    vol2_average = ma5(quotes_list, -6, -2, "volume")
    vol3_average = ma5(quotes_list, -7, -3, "volume")

    close2_average = ma5(quotes_list, -6, -2, "close")
    close3_average = ma5(quotes_list, -7, -3, "close")
    # 前天跌，昨天跌到底，今天高开高走
    # 成交量较前五天平均值收缩
    if q1_l >= q2_h and q3_l >= q2_h and q2_t < 0 and q1_t > 0 and vol3_average > vol2_average and close3_average >= close2_average:
        c1 = (q1_l - q2_h) / q2_h
        c2 = (q3_l - q2_h) / q2_h
        c3 = (q1_h - q1_l) / q2['close']
        c4 = (vol3_average - vol2_average) / vol2_average
        return {
            'trend_before': trend_before(quotes_list),
            'color': 1,
            'score': round((c1 + c2 + c3 + c4) * 1000, 2)
        }
    # 前天跌，昨天低开高走，今天涨
    # 成交量较前五天平均值增加
    elif q1_l >= q2_h and q3_l >= q2_h and q2_t > 0 and q1_t > 0 and vol2_average < vol3_average and close3_average >= close2_average:
        c1 = (q1_l - q2_h) / q2_h
        c2 = (q3_l - q2_h) / q2_h
        c3 = (q1_h - q1_l) / q2['close']
        c4 = (vol2_average - vol3_average) / vol3_average
        return {
            'trend_before': trend_before(quotes_list),
            'color': 1,
            'score': round((c1 + c2 + c3 + c4) * 1000, 2)
        }
    else:
        return False

def is_cross_shape(quotes):
    '''底部缩量的十字星线'''
    # 趋势 跌
    trendb = trend_before(quotes)
    if trendb > 0:
        return False
    # 成交量趋势 跌
    val_trend = trend_before(quotes, item='volume')
    if val_trend >= 0:
        return False

    q = quotes[-1]
    color = 1
    line = q['high'] - q['low']  # 线高
    high = q['close']
    if q['open'] > q['close']:
        color = -1
        high = q['open']
    score = round(line / q['low'] / 2 * 1000, 2)
    # 十字, 非一字板，非T字, 分数低于15舍弃，十字数量太多
    if q['open'] == q['close'] and line != 0 and q['high'] != high and score > 15:
        return {
            'trend_before': trendb,
            'color': color,
            'score': score
        }
    else:
        return False

def ma5(quotes, sindex=-5, eindex=-1, item="close"):
    count = 0
    for i in range(sindex, eindex+1):
        count += quotes[i][item]
    return count / 5

def ma5_avg(quotes, sindex=-5, eindex=-1, item="close"):
    '''
    Pervious 5 day md5 average
    :param quotes:
    :param sindex:
    :param eindex:
    :param item:
    :return:
    '''
    count = 0
    for i in range(sindex, eindex+1):
        count += ma5(quotes, i-4, i, item)
    return count / 5

def trend_before(quotes, sindex=-1, item="close"):
    '''
    计算ma5的均线趋势，计算前5天ma5均值的平均值，与后一天收盘价比较，5%以内视为横盘
    :param quotes: 行情list
    :param startIndex:
    :param item:
    :return: 0：横盘， 1：raise， -1：drop
    '''
    avg_previous_5 = ma5_avg(quotes, sindex=sindex-5, eindex=sindex-1, item=item)
    yesterday = quotes[-1]["close"]
    if avg_previous_5 > yesterday:
        ratio = (avg_previous_5 - yesterday) / avg_previous_5
        if ratio < 0.05:
            return 0
        else:
            return -1
    else:
        ratio = (yesterday - avg_previous_5) / yesterday
        if ratio < 0.05:
            return 0
        else:
            return 1

def top(d1, d2):
    if d1 > d2:
        return d1
    else:
        return d2

def bottom(d1, d2):
    if d1 > d2:
        return d2
    else:
        return d1
