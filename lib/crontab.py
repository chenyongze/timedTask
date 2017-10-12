#-*- coding:utf-8 -*-
'''
@author: yongze.chen
@summary: 解析任务执行时间配置模块
1.解析配置中六个时区参数(秒 分 时 日 月 周)，生成对应的取值列表
2.将时间戳与配置时区列表值对比，判断该时间戳是否在配置设定的时间范围内
'''
import re,time

def handle_num(val, ranges=(0, 100), res=list()):
    """处理纯数字"""
    val = int(val)
    if val >= ranges[0] and val <= ranges[1]:
        res.append(val)
    return res
 
def handle_nlist(val, ranges=(0, 100), res=list()):
    """处理数字列表 如 1,2,3,6"""
    val_list = val.split(',')
    for tmp_val in val_list:
        tmp_val = int(tmp_val)
        if tmp_val >= ranges[0] and tmp_val <= ranges[1]:
            res.append(tmp_val)
    return res
 
def handle_star(val, ranges=(0, 100), res=list()):
    """处理星号"""
    if val == '*':
        tmp_val = ranges[0]
        while tmp_val <= ranges[1]:
            res.append(tmp_val)
            tmp_val = tmp_val + 1
    return res

def handle_starnum(val, ranges=(0, 100), res=list()):
    """星号/数字 组合 如 */3"""
    tmp = val.split('/')
    val_step = int(tmp[1])
    if val_step < 1:
        return res
    val_tmp = int(tmp[1])
    while val_tmp <= ranges[1]:
        res.append(val_tmp)
        val_tmp = val_tmp + val_step
    return res

def handle_range(val, ranges=(0, 100), res=list()):
    """处理区间 如 8-20"""
    tmp = val.split('-')
    range1 = int(tmp[0])
    range2 = int(tmp[1])
    tmp_val = range1
    if range1 < 0:
        return res
    while tmp_val <= range2 and tmp_val <= ranges[1]:
        res.append(tmp_val)
        tmp_val = tmp_val + 1
    return res

def handle_rangedv(val, ranges=(0, 100), res=list()):
    """处理区间/步长 组合 如 8-20/3 """
    tmp = val.split('/')
    range2 = tmp[0].split('-')
    val_start = int(range2[0])
    val_end = int(range2[1])
    val_step = int(tmp[1])
    if (val_step < 1) or (val_start < 0):
        return res
    val_tmp = val_start
    while val_tmp <= val_end and val_tmp <= ranges[1]:
        res.append(val_tmp)
        val_tmp = val_tmp + val_step
    return res

#***********************************************
#配置时间参数各种写法 的 正则匹配
PATTEN = {
    #纯数字
    'number':'^[0-9]+$',
    #数字列表,如 1,2,3,6
    'num_list':'^[0-9]+([,][0-9]+)+$',
    #星号 *
    'star':'^\*$',
    #星号/数字 组合，如 */3
    'star_num':'^\*\/[0-9]+$',
    #区间 如 8-20
    'range':'^[0-9]+[\-][0-9]+$',
    #区间/步长 组合 如 8-20/3
    'range_div':'^[0-9]+[\-][0-9]+[\/][0-9]+$'
    #区间/步长 列表 组合，如 8-20/3,21,22,34
    #'range_div_list':'^([0-9]+[\-][0-9]+[\/][0-9]+)([,][0-9]+)+$'
}
#各正则对应的处理方法
PATTEN_HANDLER = {
    'number'   :handle_num,
    'num_list' :handle_nlist,
    'star'     :handle_star,
    'star_num' :handle_starnum,
    'range'    :handle_range,
    'range_div':handle_rangedv
}
#***********************************************    
def handle_conf(conf, ranges=(0, 100), res=list()):
    """解析配置六个时间参数中的任意一个"""
    #去除空格，再拆分
    conf = conf.strip(' ').strip(' ')
    conf_list = conf.split(',')
    other_conf = []
    number_conf = []
    for conf_val in conf_list:
        if re.match(PATTEN['number'], conf_val):
            #记录拆分后的纯数字参数
            number_conf.append(conf_val)
        else:
            #记录拆分后纯数字以外的参数，如通配符 * , 区间 0-8, 及 0－8/3 之类
            other_conf.append(conf_val)
    if other_conf:
        #处理纯数字外各种参数
        for conf_val in other_conf:
            for key, ptn in PATTEN.items():
                if re.match(ptn, conf_val):
                    res = PATTEN_HANDLER[key](val=conf_val, ranges=ranges, res=res)
    if number_conf:
        if len(number_conf) > 1 or other_conf:
            #纯数字多于1，或纯数字与其它参数共存，则数字作为时间列表
            res = handle_nlist(val=','.join(number_conf), ranges=ranges, res=res)
        else:
            #只有一个纯数字存在，则数字为时间 间隔
            res = handle_num(val=number_conf[0], ranges=ranges, res=res)
    return res

def parse_conf_time(conf_string):
    """
    Desc:解析任务时间配置参数
    Args:
        conf_string 配置内容(共六个值：秒 分 时 日 月 周) 取值范围 {秒:0-59 分:0-59 时:1-23 日:1-31 月:1-12 周:0-6(0表示周日)}
    Return:
        errcode 错误码
        cron_range list格式，秒 分 时 日 月 周 六个传入参数分别对应的取值范围
    """
    time_limit    = ((0, 59), (0, 59), (0, 23), (1, 31), (1, 12), (0, 6))
    cron_range = []
    clist = []
    conf_length   = 6
    tmp_list = conf_string.split(' ')
    for val in tmp_list:
        if len(clist) == conf_length:
            break
        if val:
            clist.append(val)
 
    if len(clist) != conf_length:
        return -1, 'config error whith [%s]' % conf_string
    cindex = 0
    for conf in clist:
        res_conf = []
        res_conf = handle_conf(conf, ranges=time_limit[cindex], res=res_conf)
        if not res_conf:
            return -1, 'config error whith [%s]' % conf_string
        cron_range.append(res_conf)
        cindex = cindex + 1
    return 0, cron_range

def time_match_conf(crontab_range, time_stamp):
    """
    Desc:将时间戳与配置中一行时间参数对比，判断该时间戳是否在配置设定的时间范围内
    Args:
        crontab_time: crontab配置中的五个时间（秒 分 时 日 月 周)参数对应时间取值范围
        time_stamp  : 某个整型时间戳，如：1375027200
    Return: True / False
    """
    #把时间戳改成对应的[秒,分,时,日,月,周]
    time_obj    = time.localtime(time_stamp)
    time_struct = [time_obj.tm_sec, time_obj.tm_min, time_obj.tm_hour, time_obj.tm_mday, time_obj.tm_mon, time_obj.tm_wday]
    
    cindex = 0
    for val in time_struct:
        if val not in crontab_range[cindex]:
            return False
        cindex = cindex + 1
    return True

"""
#程序测试
conf_string= "*/5 * * * * *"
errcode, crontab_range  = parse_conf_time(conf_string)
if errcode==0:
    for item in crontab_range:
        print item

time_stamp = int(time.time())
print time_stamp

time_obj    = time.localtime(time_stamp)
print [time_obj.tm_sec, time_obj.tm_min, time_obj.tm_hour, time_obj.tm_mday, time_obj.tm_mon, time_obj.tm_wday]
        
errcode, result = time_match_conf(crontab_range, time_stamp)
if errcode==0:
    print result
"""