# -*- coding:utf-8 -*-
'''
@summary: 配置加载模块
@author: kevenchen
'''
import os,re,json
import lib.file

BasePath        = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir)).replace("\\", "/")
BasePath_Config = BasePath+'/config'
BasePath_Lib    = BasePath+'/lib'
BasePath_Mod    = BasePath+'/mod'
BasePath_Job    = BasePath+'/job'
BasePath_Cache  = BasePath+'/cache'
BasePath_Log    = BasePath_Cache+'/log'

def load(file_name,path='/',defval=''):
    file_path       = lib.config.BasePath_Config+'/'+file_name+'.json'
    if os.path.exists(file_path)==False:
        print 'config %s not exist'%file_name
        return defval
    file_content    = lib.file.read(file_path)
    file_content    = re.sub(r'\/\*.*\*\/','',file_content)
    file_content    = re.sub(r'\/\/.*\n','\n',file_content)
    try:
        config_json = json.loads(file_content)
    except:
        print 'config %s json format error'%file_name
        return defval
    
    path=path.strip('/')
    if path=='':
        return config_json
    else:
        path_key=path.split('/')
        path_val=config_json
        for key in path_key:
            if key in path_val:
                path_val=path_val[key]
            else:
                return defval
    return path_val
