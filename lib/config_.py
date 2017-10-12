# -*- coding:utf-8 -*-
'''
@summary: 配置解析模块
@author: kevenchen
'''
import ConfigParser
import os

BasePath        = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir)).replace("\\", "/")
BasePath_Config = BasePath+'/config'
BasePath_Lib    = BasePath+'/lib'
BasePath_Mod    = BasePath+'/mod'
BasePath_Job    = BasePath+'/job'

BasePath_Cache = BasePath+'/cache'
BasePath_Log    = BasePath_Cache+'/log'


def load(ini_name,section_name=''):
    global BasePath_Config
    field_path="%s/%s.ini"%(BasePath_Config,ini_name)
    cf = MyConfigParser()
    cf.read(field_path)
    
    result={}
    sections = cf.sections()
    for section in sections:
        if section not in result:
            result[section]={}
        items = cf.items(section)
        for item in items:
            result[section][item[0]]=item[1]

    if section_name=='':
        return result
    else:
        if section_name in result:
            return result[section_name]
        else:
            return {}
        
class MyConfigParser(ConfigParser.ConfigParser):  
    def __init__(self,defaults=None):  
        ConfigParser.ConfigParser.__init__(self,defaults=None)  
    def optionxform(self, optionstr):  
        return optionstr  