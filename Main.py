import ctypes, sys # Must have to run as Administrator
from EvtReader import *

def is_admin(): #Run ad admin
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() #Check if user admin
    except:
        return False

#Start from here
if is_admin(): #If Admin - Run this->
    GetEvents() #Getting Events to class format --Need to brodcast using protobuf

else: #If not admin - Run as admin  #Re-run the program with admin rights
   ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable,__file__, None, 1)






