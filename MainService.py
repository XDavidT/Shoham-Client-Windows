import ctypes, sys  # Must have to run as Administrator
import servicemanager, win32event, win32service,win32serviceutil
import threading
import win32evtlog # requires pywin32 pre-installed
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

class SiemService(win32serviceutil.ServiceFramework):
    _svc_name_ = SIEM_SRV_NAME
    _svc_display_name_ = SIEM_NAME
    _svc_description_ = 'Python Service Description'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.alive = None

    def SvcStop(self):
        self.alive = False
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)     # Status: Service Stopped
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)    # Status: Service Starting.....
        self.alive = True
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        cat_to_run = ['Security', 'System']  # need to get from outside
        evtMgr = evtmanager_pb2.evtMgr()
        threads = list()    # Must declare to use
        # Start socket
        try:
            for log_type in cat_to_run:
                curr_thr = threading.Thread(target=self.GetEvents,args=(evtMgr,log_type))
                threads.append(curr_thr)
                curr_thr.start()
        except:  # When it fail, pop-up massage will
            print("error in thread")
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)          # Status: Service Running
        rc = None
        while rc != win32event.WAIT_OBJECT_0:  # Wait until the "Stop"
            rc = win32event.WaitForSingleObject(self.hWaitStop, 5000)
        for thread in threads:  # If service was stopped, close all threads
            thread.join()
        # Stop socket
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #

    def GetEvents(self, evtmgr, log_type):
        self.clearEvt(log_type)
        hand = win32evtlog.OpenEventLog("localhost", log_type)  # Handle the connection
        flags = win32evtlog.EVENTLOG_FORWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        last_check = win32evtlog.GetNumberOfEventLogRecords(hand)

        # This while must stop when service is stopped #
        while self.keepAlive():
            curr_check = win32evtlog.GetNumberOfEventLogRecords(hand)
            if curr_check > last_check:
                events = win32evtlog.ReadEventLog(hand, flags, curr_check)
                for event in events:
                    evtmgr.id = event.EventID
                    evtmgr.time.FromDatetime(event.TimeGenerated)
                    evtmgr.type = event.EventType
                    evtmgr.src = event.SourceName
                    evtmgr.cat = event.EventCategory
                    data = event.StringInserts
                    if data:
                        for msg in data:
                            data_input = evtmgr.dataList.add()
                            data_input.data = msg
                    last_check = curr_check



    def clearEvt(self,log_type):
        hand = win32evtlog.OpenEventLog("localhost", log_type)  # Handle the Event Viewer
        win32evtlog.ClearEventLog(hand, None)

    def keepAlive(self):    # Manage the thread's
        return self.alive


# + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +#
# pyinstaller -F --hidden-import=win32timezone --name=MyService MainService.py evtmanager_pb2.py

# Program Declaration
# Step 1 - Start from main
if __name__ == '__main__':
    # Step 2 checking for arguments got in command line
    if len(sys.argv) == 1:
        # Step 3 - check user is Admin
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