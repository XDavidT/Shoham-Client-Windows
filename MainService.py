import ctypes, sys  # Must have to run as Administrator
import time

import servicemanager, win32event, win32service,win32serviceutil,win32evtlog
import threading
import socket,getpass,platform
import grpc
from clientConnection import *
from ProtoBuf import evtmanager_pb2_grpc,evtmanager_pb2
from getmac import get_mac_address

SIEM_NAME = "My Service Name"
SIEM_SRV_NAME = "MyServiceName"

#   Function Declaration  #

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
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)    # Status: 'Service Starting.....'
        self.alive = True                                               # Internal status to my functions
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, # Open Event Viewer to logs
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))

        evtMgr = evtmanager_pb2.evtMgr()    # Proto
        threads = list()    # Must declare to use thread list

        try:   #   This 'try' is locate problems in connection

            con = connection()     # Open Socket (gRPC)
            informationMsg = con.getCategory()   # Server side function
            cat_to_run = informationMsg.category                                # Return category list

            try:
                for log_type in cat_to_run:                                     # Open thread by log types
                    curr_thr = threading.Thread(target=self.GetEvents,args=(evtMgr,log_type,con.stub))
                    threads.append(curr_thr)
                    curr_thr.start()
            except:  # When it fail, pop-up massage will
                print("error in thread.")    # Debug print
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)          # Status: Service Running
            print("Service is running !!")   # Debug print

            # --- From here service wait to "stop" command --- #
            rc = None
            while rc != win32event.WAIT_OBJECT_0:  # Wait until the "Stop"
                rc = win32event.WaitForSingleObject(self.hWaitStop, 5000)
            for thread in threads:  # If service was stopped, close all threads
                thread.join()
            con.shutdown()

        except:
            print("Error in connection (to open stub)\nRetry in 3 second")
            time.sleep(3)
            return self.SvcDoRun()
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #

    def GetEvents(self, evtmgr, log_type,stub):
        self.clearEvt(log_type)
        hand = win32evtlog.OpenEventLog("localhost", log_type)  # Handle the connection to EventViewer
        flags = win32evtlog.EVENTLOG_FORWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        last_check = win32evtlog.GetNumberOfEventLogRecords(hand)

        evtmgr.hostname = socket.gethostname()  # Using Socket we can know the PC name
        evtmgr.username = getpass.getuser()     # Using getpass we can know what user is current using
        evtmgr.os = platform.system()           # Using platform to get OS brand
        evtmgr.ip_add = socket.gethostbyname(evtmgr.hostname) # Get the IP Address from socket
        evtmgr.mac_add = get_mac_address(ip=(socket.gethostbyname(evtmgr.hostname))) # Get the MAC Address
        print("%s is up and running !" % log_type) # Debug print

        # ! Important: This while must stop when service is stopped ! #
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
                    data_list = evtmgr.dataList
                    if data:
                        for msg in data:
                            data_list.append(msg)
                    # Push log return true if completed
                    if(stub.PushLog(evtmgr)):   # Debug in gRPC to return value
                        last_check = curr_check
                    else:
                        print("error pushing %d" % evtmgr.id) # Debug print

    def clearEvt(self,log_type):
        hand = win32evtlog.OpenEventLog("localhost", log_type)  # Handle the Event Viewer
        win32evtlog.ClearEventLog(hand, None)

    def keepAlive(self):    # Manage the thread's
        return self.alive

# + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +#
# pyinstaller -F --hidden-import=win32timezone --hidden-import=pkg_resources --name=MyService MainService.py clientConnection.py Protobuf/evtmanager_pb2.py ProtoBuf/evtmanager_pb2_grpc.py

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

