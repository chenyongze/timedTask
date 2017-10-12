# -*- coding:utf-8 -*-
import lib.database

def run(params):
    db = lib.database.load(dbname='devicecenter')
    
    table='device_info'
    field="ServerId,ServerAsSetId,ServerIP"
    
    #单条记录查询
    where={"ServerId":"12315"}
    info = db.select_info(where,table,field)
    print info
    #多条记录查询
    where={"ServerAsSetId like ":"%TYSV08065287%"}
    rows = db.select_list(where,table,field)
    print rows
    #插入多条数据
    data=[
        {"ServerId":100,"ServerAsSetId":"TYSV100","ServerIP":"11.129.129.159"},
        {"ServerId":101,"ServerAsSetId":"TYSV101","ServerIP":"11.129.129.160"}
    ]
    db.insert_data(data,table)
    #修改数据
    data={"ServerAsSetId":"TYSV100","ServerIP":"12.129.129.159"},
    where={"ServerId":100}
    db.update_data(data,where)
    #删除数据
    where={"ServerId":100}
    db.delete_data(where,table)
