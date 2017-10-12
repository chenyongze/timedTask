## timedTask
#### 秒级定时任务框架
#### 使用教程
##### 一、程序目录：

```
    cache //缓存
        |--job              //[目录]存放任务状态文件
        |--log              //[目录]存放任务执行日志文件
            |--log_20160527 //[文件]任务执行日志
        |--pid              //[文件]保存当前守护进程PID
    config //配置
        |--database.json    //[文件]数据库配置文件
    lib //框架库
        |--__init__.py
        |--config.py        //获取ini配置模块
        |--crontab.py       //解析任务配置文件setting.json模块
        |--daemon.py        //守护进程模块
        |--database.py      //数据库操作模块
        |--file.py          //文件操作模块
        |--log.py           //日志操作模块
    mod //任务通用模块
        |--__init__.py
        |--tmp.py
    job //任务代码
        |--__init__.py
        |--job_test1.py     //执行任务1
        |--job_test2.py     //执行任务2
    setting.json            //任务执行配置文件
    main.py                 //主入口程序
```

##### 二、配置文件(setting.json)
```
    {
        "job_test1":{
            "cron_time"         : "* * * * * *", // 配置 秒 分 时 日 月 周
            "timeout"           : "3", // 超时时间
            "params"            : {"begin":"0","end":"999"},
            "alarm_fail_total"  : "1",//任务失败累计1次 
            "alarm_fail_range"  : "3600",//任务在3600秒之后，失败累计清0
            "alarm_adminlist"   : "yongze.chen",
            "alarm_notice_mode" : "SMG;RTX;NOC",
            "alarm_message"     : "告警提示内容"
        },
        "job_test2":{
            "cron_time" : "*/2 * * * * *",
            "timeout"   : "6",
            "params"    : {}
        }
    }
```
##### 三、数据库配置(database.json)
```
    {
        "devicecenter":{
            "host"      : "127.0.0.1",
            "port"      : "3306",
            "user"      : "root",
            "passwd"    : "root",
            "dbname"    : "devicecenter",
            "tblprefix" : "t_",
            "charset"   : "utf8"
        }   
    } 
```

##### 四、任务编写(job_test1.py)
```python
    '''
    # -*- coding:utf-8 -*-
    '''
    @author: yongze.chen
    @summary: 测试任务1
    '''
    #加载lib/database.py模块
    import lib.database
    '''
    必须定义run函数才能被引擎调度,参数params传递的是配置（setting.json）中的params配置
    '''
    def run(params):
        db = lib.database.load(dbname='devicecenter')
    
        table = "device_info"
        field = "ServerId,ServerAsSetId,ServerIP"
    
        #单条记录查询
        where={"ServerId":"12315"}
        info = db.select_info(where,table,field)

        #多条记录查询
        where={"ServerAsSetId like ":"%TYSV08065287%"}
        rows = db.select_list(where,table,field)

        #插入多条数据########################
        data=[
            {"ServerId":100,"ServerAsSetId":"TYSV100","ServerIP":"11.129.129.159"},
            {"ServerId":101,"ServerAsSetId":"TYSV101","ServerIP":"11.129.129.160"}]
        db.insert_data(data,table)

        #修改数据########################
        data={"ServerAsSetId":"TYSV100","ServerIP":"12.129.129.159"},
        where={"ServerId":100}
        db.update_data(data,where)

        #删除数据########################
        where={"ServerId":100}
        db.delete_data(where,table)
```

##### 五、运行任务引擎
```shell
    puthon main.py start        #任务引擎开启
    python main.py restart      #任务引擎重启
    python main.py stop         #任务引擎关闭
```

##### 六、查看运行日志
```shell
    tail -f -n20 ./cache/log/log_20160527
```
