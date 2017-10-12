# -*- coding:utf-8 -*-
'''
@summary: 数据库操作
@author: yongze.chen
'''
import MySQLdb
import lib.config
dbs={}

def load(dbname,table='',field='*'):
    if dbname not in dbs:
        dbs[dbname]=db_mysql(dbname,table,field)
    return dbs[dbname]

def unload(dbname):
    if dbname in dbs:
        dbs.pop(dbname)
    
def create(dbname,table='',field='*'):
    return db_mysql(dbname,table,field)

#Mysql数据库ORM类
class db_mysql:
    con=None
    cur=None
    auto_commit=True
    table_prefix=''
    
    dbname=''
    table=''
    field='*'
    
    last_sql=''
    
    def __init__(self,dbname,table='',field='*'):
        db_config=lib.config.load('database',dbname)
        
        if len(db_config)<=0 :
            return None;
        
        self.dbname=db_config['dbname']
        self.con=MySQLdb.connect(
            host    = db_config['host'],
            port    = int(db_config['port']),
            user    = db_config['user'],
            passwd  = db_config['passwd'],
            db      = db_config['dbname'],
            charset = db_config['charset']
        )
        if 'tblprefix' in db_config:
            self.table_prefix=db_config['tblprefix']
        if self.auto_commit:
            self.con.autocommit(1)
        else:
            self.con.autocommit(0)
        self.cur=self.con.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        self.cur.execute('set names %s'%(db_config['charset'],))
        
        self.table=self.get_table(table)
        self.field=self.get_field(field,table)

        '''
        try:

        except:
            print u"Error:数据库链接失败"
            exit()
        '''
        
    def select_info(self,where={},table='',field='*'):
        table=self.get_table(table)
        field=self.get_field(field,table)
        sql="select %s from %s %s limit 1"%(field,table,self.build_where(where))
        self.cur.execute(sql)
        self.last_sql=sql
        return self.cur.fetchone()
    
    def select_list(self,where={},order={},table='',field='*'):
        table=self.get_table(table)
        field=self.get_field(field,table)
        sql="select %s from %s %s "%(field,table,self.build_where(where))
        if order and len(order)>0:
            orders=""
            for (k,v) in order.iteritems():
                orders+=" %s %s,"%(k,v)
            sql+=" order by "+orders.rstrip(',')
            
        self.cur.execute(sql)
        self.last_sql=sql
        return self.cur.fetchall()
    
    def select_page(self,page={"index":1,"size":100},where={},order={},table='',field='*'):
        table=self.get_table(table)
        field=self.get_field(field,table)
        sql="select SQL_CALC_FOUND_ROWS %s from %s %s "%(field,table,self.build_where(where))
        if order and len(order)>0:
            orders=""
            for (k,v) in order.iteritems():
                orders+=" %s %s,"%(k,v)
            sql+=" order by "+orders.rstrip(',')
        star  = page["size"]*(page["index"]-1)
        offs  = page["size"]
        sql+=" limit %s,%s"%(star,offs)
        self.cur.execute(sql)
        data=self.cur.fetchall()
        self.cur.execute('SELECT FOUND_ROWS() as total')
        total=self.cur.fetchone().get('total')
        return {"data":data,"total":total}
    
    def update_data(self,info,where,table='',field='*'):
        table=self.get_table(table)
        field=self.get_field('*',table)
        field_list=field.split(',')
        
        if len(info)<=0:
            return False
        sql='update '+table+' set '
        for (k,v) in info.iteritems():
            if k in field_list:
                sql+="%s='%s',"%(k,v)
        sql=sql.rstrip(',')
        sql_where=self.build_where(where)
        if sql_where!='':
            sql+=sql_where
        else:
            sql+=' where 0'#避免不带where条件操作
        self.cur.execute(sql)
        self.last_sql=sql
        return True
    
    def insert_data(self,data,table='',field='*'):
        table=self.get_table(table)
        field=self.get_field(field,table)
        field_list=field.split(',')
        
        if len(data)<=0:
            return False
        sql="insert into %s "%(table,)
        fields=""
        values=""
        if isinstance(data,dict):
            #一维数组
            keys=filter(lambda x: x in field_list, data.keys())
            vals=[]
            for (k,v) in data.iteritems():
                if k in keys:
                    if isinstance(v,list):
                        v=';'.join(v)
                    else:
                        v=unicode(v)
                    vals.append(v)
            fields='('+(','.join(keys))+')'
            values="('"+("','".join(vals))+"')"
        else:
            #二维数组
            keys=filter(lambda x: x in field_list, data[0].keys())
            fields='('+','.join(keys)+')'
            for info in data:
                vals=[]
                for (k,v) in info.iteritems():
                    if k in keys:
                        if isinstance(v,list):
                            v=';'.join(v)
                        else:
                            v=unicode(v)
                        vals.append(v)
                values+="('"+("','".join(vals))+"'),"                
            values=values.rstrip(',')
        sql+=fields+' values'+values
        self.cur.execute(sql)
        self.last_sql=sql
        sql="select last_insert_id() as id"
        self.cur.execute(sql)
        result=self.cur.fetchone()
        return result['id']
    
    def replace_data(self,data,table='',field='*'):
        table=self.get_table(table)
        field=self.get_field(field,table)
        field_list=field.split(',')
        
        if len(data)<=0:
            return False
        sql="replace into %s "%(table,)
        fields=""
        values=""
        if isinstance(data,dict):
            #一维数组
            keys=filter(lambda x: x in field_list, data.keys())
            vals=[]
            for (k,v) in data.iteritems():
                if k in keys:
                    if isinstance(v,list):
                        v=';'.join(v)
                    else:
                        v=unicode(v)
                    vals.append(v)
            fields='('+(','.join(keys))+')'
            values="('"+("','".join(vals))+"')"
        else:
            #二维数组
            keys=filter(lambda x: x in field_list, data[0].keys())
            fields='('+','.join(keys)+')'
            for info in data:
                vals=[]
                for (k,v) in info.iteritems():
                    if k in keys:
                        if isinstance(v,list):
                            v=';'.join(v)
                        else:
                            v=unicode(v)
                        vals.append(v)
                values+="('"+("','".join(vals))+"'),"                
            values=values.rstrip(',')
        sql+=fields+' values'+values
        self.cur.execute(sql)
        self.last_sql=sql
        return True
    
    def delete_data(self,where,table=''):
        table=self.get_table(table)
        sql_where=self.build_where(where)
        if sql_where=='':
            sql_where=' where 0 '
        sql="delete from %s %s"%(table,sql_where)
        self.cur.execute(sql)
        self.last_sql=sql
        return True
        
    def exec_sql(self,sql):
        self.cur.execute(sql)
        self.last_sql=sql
        return self.cur.fetchall()
    
    def get_table(self,table):
        if table=='':
            return self.table
        else:
            if self.table_prefix!='' and table.find(self.table_prefix)!=0:
                return self.table_prefix+table
            else:
                return table
        
    def get_field(self,field,table=''):
        table=self.get_table(table)
        if table=='':
            return field
        
        if field=='' or field=='*' :
            if table==self.table and self.field not in ('','*'):
                field=self.field
            else:
                sql="select group_concat(COLUMN_NAME) as table_field from information_schema.COLUMNS "
                sql+=" where table_name = '%s' and table_schema = '%s'"%(table,self.dbname)
                self.cur.execute(sql)
                info=self.cur.fetchone()
                if len(info)>0:
                    field=info['table_field']
                    
        return field
    
    def build_where(self,where):
        sql=""
        count=0
        for key,val in where.iteritems():
            if count==0:
                sql+=" where "
            else:
                sql+=" and "
            if isinstance(val,list)==False:
                if key.find(' ')>0:
                    sql+=" %s '%s'"%(key,val)
                else:
                    sql+=" %s = '%s'"%(key,val)
            else:
                vals=map(lambda x:str(x),val)
                vals="'"+("','".join(vals))+"'"
                sql+=" %s in (%s)"%(key,vals)
        return sql
    
    def get_last_sql(self):
        return self.last_sql
    
    def distroy(self):
        #unload(self.dbname)
        if self.cur:
            self.cur.close()
            self.cur=None
        if self.con:
            self.con.close()
            self.con=None
            
    
    def __del__(self):
        self.distroy()
    
    