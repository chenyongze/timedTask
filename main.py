# -*- coding:utf-8 -*-
import os,sys,imp,time,json,re
import multiprocessing
import lib.daemon
import lib.config_
import lib.crontab
import lib.file
import lib.log

from _random import Random
# start run
app_name = "timedTask"
pid_file = lib.config_.BasePath_Cache+'/pid'

def get_job_status(cron_name):
    job_file  = lib.config_.BasePath_Cache+'/job/'+cron_name+'.log'
    job_file_content = lib.file.read(job_file, 'line')
    job_status = {"pid":0,"locked":False,"lasttime":0,"fail_begin":0,"fail_count":0}
    if job_file_content.strip()!='':
        try:
            cur_status  = json.loads(job_file_content)
            job_status.update(cur_status)
        except:
            pass
    for x in ('pid','lasttime','fail_begin','fail_count'):
        job_status[x]=int(job_status[x])
    return job_status
    
def set_job_status(cron_name,cron_options,pid,locked,success):
    job_file   = lib.config_.BasePath_Cache+'/job/'+cron_name
    
    job_status = get_job_status(cron_name)
    
    time_stamp= int(time.time())
    
    new_status={}
    new_status['pid']       = int(pid)
    new_status['locked']    = locked
    new_status['lasttime']  = time_stamp
    if success:
        new_status['fail_begin']=job_status['fail_begin']
        new_status['fail_count']=job_status['fail_count']
    else:
        fail_begin=job_status['fail_begin']
        fail_count=1
        if time_stamp-job_status['fail_begin']>=cron_options['alarm_fail_range']:
            fail_begin=time_stamp
        else:
            fail_count=job_status['fail_count']+1
            
        new_status['fail_begin']=fail_begin
        new_status['fail_count']=fail_count
    
    if new_status['fail_count']==cron_options['alarm_fail_total']:
        #发出告警处理逻辑
        lib.log.add(cron_name+' alarm ',"log_%Y%m%d")
        
    lib.file.write(job_file,json.dumps(new_status))

def chk_job_setting():
    try:
        content = lib.file.read(lib.config_.BasePath+'/setting.json')
        content=re.sub(r'\/\*.*\*\/','',content)
        content=re.sub(r'\/\/.*\n','\n',content)
        cronjobs=json.loads(content)
        if len(cronjobs)<=0:
            return False,'Not cronjob start!'
        else:
            msg="";
            for cron_name,cron_options in cronjobs.items():
                msg+= cron_options['cron_time']+"\t"+cron_name+"\t"+json.dumps(cron_options['params'])+"\n"
            return True,msg
    except:
        return False,"setting.json json format error!"
    
def get_job_setting():
    cronjobs={}
    defaults={
            "cron_time" : "* * * * * *",
            "timeout"   : 0,
            "params"    : {},
            "alarm_fail_total":0,
            "alarm_fail_range":0,
            "alarm_adminlist":"",
            "alarm_notice_mode":"",
            "alarm_message":""
    }

    try:
        content = lib.file.read(lib.config_.BasePath+'/setting.json')
        content=re.sub(r'\/\*.*\*\/','',content)
        content=re.sub(r'\/\/.*\n','\n',content)
        cronjobs=json.loads(content)
        for cron_name in cronjobs:
            errcode, cron_range = lib.crontab.parse_conf_time(cronjobs[cron_name]['cron_time']) 
            if errcode==0:
                cronjobs[cron_name]['cron_range'] = cron_range
            else:
                cronjobs[cron_name]['cron_range'] = []
                
            defaults.update(cronjobs[cron_name])
            for x in ('timeout','alarm_fail_total','alarm_fail_range'):
                defaults[x]=int(defaults[x])
                
            cronjobs[cron_name]=defaults.copy()
    except:
        cronjobs = {}
    
    return cronjobs

def job_worker(cron_name,cron_options):
    try:
        pid=os.getpid()
        #加任务锁
        set_job_status(cron_name,cron_options,pid,True,True)
        
        fp, pathname, desc = imp.find_module(cron_name, [lib.config_.BasePath_Job])
        job_obj = imp.load_module(cron_name, fp, pathname, desc)
        params={}
        if 'params' in cron_options:
            params=cron_options['params']
        job_obj.run(params)
        
        #释放任务锁
        #lib.file.write(job_file, '{"pid":"'+str(pid)+'","locked":false,"lasttime":"'+str(int(time.time()))+'"}')
        set_job_status(cron_name,cron_options,pid,False,True)
        
        lib.log.add(cron_name+' run successful',"log_%Y%m%d")
        #print cron_name+' run successful ' + str(time_stamp)
    except OSError, e:
        set_job_status(cron_name,cron_options,pid,False,False)
        
        lib.log.add(cron_name+' run failed',"log_%Y%m%d")
        #print cron_name+' run failed' + str(time_stamp)

def job_start(cron_name,cron_options,time_stamp):
    if os.path.exists(lib.config_.BasePath_Job+'/'+cron_name+'.py')==False:
        return False
    
    timeout=0
    if 'timeout' in cron_options:
        timeout = int(cron_options['timeout'])
    
    #获取任务运行态参数
    job_status=get_job_status(cron_name)
        
    #时间重叠,不执行
    if job_status['lasttime']==time_stamp:
        return False
    
    #没有超时的情况下
    if (time_stamp-job_status['lasttime'])<timeout:
        #任务加锁,不执行
        if job_status['locked']==True:
            return False
    else:
        #超时的情况下，尝试着结束上一个进程任务
        set_job_status(cron_name,cron_options,0,False,False)
        if job_status['pid']>0:
            try:
                #for i in range(0,10):
                os.kill(job_status['pid'], 9)                
            except:
                pass
        return False
            
    p=multiprocessing.Process(target = job_worker, args = (cron_name,cron_options) )
    p.daemon=False
    p.start()
    
    return True

def job_stop():
    dirname = lib.config_.BasePath_Cache+'/job'
    dirlist = lib.file.scandir(dirname)
    for filename in dirlist:
        job_file_content=lib.file.read(filename,'line').strip()
        job_info= json.loads(job_file_content)
        job_pid = 0
        if 'pid' in job_info:
            job_pid = int(job_info['pid'])

        if job_pid>0:
            try:
                os.kill(job_pid, 9)
            except:
                pass
        lib.file.remove(filename)

class ctdaemon(lib.daemon.daemon):
    def _run(self):
        cronjobs=get_job_setting()
        while True:
            time_stamp = int(time.time())
            for cron_name,cron_options in cronjobs.items():
                if lib.crontab.time_match_conf(cron_options['cron_range'], time_stamp):
                    job_start(cron_name,cron_options,time_stamp)
            time.sleep(0.2);
                    
    def stop(self):
        job_stop()
        super(ctdaemon,self).stop()

'''
res,msg=chk_job_setting()
if res:
    print msg
else:
    print msg
    exit()

cronjobs=get_job_setting()
if len(cronjobs)>0:
    for cron_name in cronjobs:
        errcode, cron_range = lib.crontab.parse_conf_time(cronjobs[cron_name]['cron_time']) 
        if errcode==0:
            cronjobs[cron_name]['cron_range'] = cron_range
        else:
            cronjobs[cron_name]['cron_range'] = []
    for i in range(0,60):
        time_stamp = int(time.time())
        for cron_name,cron_options in cronjobs.items():
            if lib.crontab.time_match_conf(cron_options['cron_range'], time_stamp):
                job_start(cron_name,cron_options,time_stamp)
        time.sleep(0.1);
        
    print 'End'
    exit()
'''               

if __name__ == "__main__":
    if len(sys.argv) == 2:
        ctdaemon_object = ctdaemon(pid_file)
        if 'start' == sys.argv[1]:
            lib.file.remove(pid_file);
            res,msg=chk_job_setting()
            if res:
                print msg
            else:
                print msg
                exit()
            ctdaemon_object.start()
        elif 'stop' == sys.argv[1]:
            ctdaemon_object.stop()
        elif 'restart' == sys.argv[1]:
            lib.file.remove(pid_file);
            res,msg=chk_job_setting()
            if res:
                print msg
            else:
                print msg
                exit()
            ctdaemon_object.restart()
        else:
            print "usage: %s start|stop|restart" % sys.argv[0]
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
