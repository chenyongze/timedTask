# -*- coding:utf-8 -*-
'''
@summary: 日志记录模块
@author: yongze.chen
'''
import time
impimport lib.config_rom compiler.pycodegen import EXCEPT

#添加日志
def add(log_content,file_name):
    log_line=time.strftime("[%Y-%m-%d %H:%M:%S]\t")+log_content+"\n"
    log_file=lib.clib.config_Path_Log+'/'+time.strftime(file_name)
    try:
        fp=open(log_file,'a+')
        fp.write(log_line)
        fp.close()
    except:
        print 'Log(%s) registration failed'%(time.strftime(file_name),)