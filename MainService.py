import ctypes, sys  # Must have to run as Administrator
import servicemanager, win32event, win32service,win32serviceutil
import _thread
from EvtReader import *
import evtmanager_pb2
SIEM_NAME = "My Service Name"
SIEM_SRV_NAME = "MyServiceName"

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

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        # Start socket
        clearEvt()  # Clear events in start - function located in 'EvtReader'
        rc = None
        while rc != win32event.WAIT_OBJECT_0:
            for srv_name in cat_to_run:
                try:
                    _thread.start_new_thread(GetEvents(evtMgr,srv_name, self.hWaitStop))
                except:
                    Mbox(SIEM_NAME+' Error', 'Fail to start thread', 0)
            rc = win32event.WaitForSingleObject(self.hWaitStop, 5000)
            # Stop socket

#-------------------------------------------------------------------------------------------------------------------#

cat_to_run = ['Security','System']
evtMgr = evtmanager_pb2.evtMgr()

# Program Declaration
# Step 1 - Start from main
if __name__ == '__main__':
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