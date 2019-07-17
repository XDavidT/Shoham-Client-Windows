import ctypes, sys  # Must have to run as Administrator
import servicemanager, win32event, win32service,win32serviceutil
import threading
from EvtReader import *
import evtmanager_pb2
SIEM_NAME = "My Service Name"
SIEM_SRV_NAME = "MyServiceName"
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# Function Declaration

# Run ad admin
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()  # Check if user admin
    except:
        return False

# Pop windows Massage box
def Mbox(title, text, style):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)

class SiemService(win32serviceutil.ServiceFramework):
    _svc_name_ = SIEM_SRV_NAME
    _svc_display_name_ = SIEM_NAME

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        print("Service creat !")

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        cat_to_run = ['Security', 'System']  # need to get from outside
        evtMgr = evtmanager_pb2.evtMgr()
        threads = list()    # Must declare to use
        # Start socket
        try:
            for srv_name in cat_to_run:
                curr_thr = threading.Thread(target=GetEvents,args=(evtMgr,srv_name))
                threads.append(curr_thr)
                curr_thr.start()
        except:  # When it fail, pop-up massage will
            Mbox(SIEM_NAME + ' Error', 'Fail to start thread', 0)
        rc = None
        while rc != win32event.WAIT_OBJECT_0:  # Wait until the "Stop"
            rc = win32event.WaitForSingleObject(self.hWaitStop, 5000)
        for thread in threads:  # If service was stopped, close all threads
            thread.join(1)
        # Stop socket


# + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +#


# Program Declaration
# Step 1 - Start from main
if __name__ == '__main__':
    if len(sys.argv) == 1:
        # Step 2 - check user is Admin
        if is_admin():  # calling function to check OR get admin access
            # Step 3 - Start the service
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(SiemService)
            servicemanager.StartServiceCtrlDispatcher()

        else:  # If not admin - Run as admin  #Re-run the program with admin rights
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    else:
        win32serviceutil.HandleCommandLine(SiemService)
else:
    win32serviceutil.HandleCommandLine(SiemService)