# -*- coding:utf-8 -*-
'''
@summary: 操作系统兼容模块
@author: yongze.chen
'''
import os

# needs win32all to work on Windows
if os.name == 'nt':
    #pywin32-220.win32-py2.7.exe
    import win32con, win32file, pywintypes
    LOCK_EX = win32con.LOCKFILE_EXCLUSIVE_LOCK
    LOCK_SH = 0 # the default
    LOCK_NB = win32con.LOCKFILE_FAIL_IMMEDIATELY
    __overlapped=pywintypes.OVERLAPPED()
    
    def flock(file, flags):
        hfile = win32file._get_osfhandle(file.fileno(  ))
        win32file.LockFileEx(hfile, flags, 0, 0xffff0000, __overlapped)

    def funlock(file):
        hfile = win32file._get_osfhandle(file.fileno(  ))
        win32file.UnlockFileEx(hfile, 0, 0xffff0000, __overlapped)
        
    def killpid(pid):
        os.popen('taskkill.exe /pid:'+str(pid)+' /f')
        
elif os.name == 'posix':
    import fcntl
    LOCK_EX = fcntl.LOCK_EX
    LOCK_SH = fcntl.LOCK_SH
    LOCK_NB = fcntl.LOCK_NB

    def flock(file, flags):
        fcntl.flock(file.fileno(), flags)

    def funlock(file):
        fcntl.flock(file.fileno(), fcntl.LOCK_UN)
    
    def killpid(pid):
        os.kill(pid, 9)
        
else:
    raise RuntimeError("The framework does not support the current operating system")
