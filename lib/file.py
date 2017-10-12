# -*- coding:utf-8 -*-
'''
@summary: 文件操作模块
@author: yongze.chen
'''
import os

#写文件内容
def write(filename,content):
    fp=open(filename,'w')
    fp.write(str(content))
    fp.close()
#读文件内容
def read(filename,mod='all'):
    if os.path.exists(filename)==False:
        return ''
    fp=open(filename,'r')
    mod=mod.lower()
    content=''
    if(mod=='lines'):
        content=fp.readlines()
    elif(mod=='line'):
        content=fp.readline()
    else:
        content=fp.read()
    fp.close()
    return content
#遍历目录
def scandir(dirname):
    result=[]
    stack=[]
    while os.path.isdir(dirname):
        filelist=os.listdir(dirname)
        for filename in filelist:
            if filename in ('.','..'):
                continue
            if os.path.isdir(dirname+'/'+filename):
                stack.append(dirname+'/'+filename)
            result.append(dirname+'/'+filename)
        if len(stack)>0:
            dirname=stack.pop()
        else:
            break
    return result

def remove(filename):
    if os.path.exists(filename):
        os.remove(filename)
    return True

