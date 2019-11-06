import ctypes, sys  # Must have to run as Administrator
import time

import servicemanager, win32event, win32service,win32serviceutil,win32evtlog
import threading
import socket,getpass,platform
import encodings.idna
from clientConnection import *
from ProtoBuf import evtmanager_pb2_grpc,evtmanager_pb2
from getmac import get_mac_address

SIEM_NAME = "Siem Example"
SIEM_SRV_NAME = "SiemExample"

#   Function Declaration  #
class SiemService(win32serviceutil.ServiceFramework):
    _svc_name_ = SIEM_SRV_NAME
    _svc_display_name_ = SIEM_NAME
    _svc_description_ = 'Python Service Description'
    _station_name_= socket.gethostname()

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.alive = None
        self.nextTry = 1

    def SvcStop(self):
        self.alive = False
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)     # Status: Service Stopped
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)    # Status: 'Service Starting.....'
        self.alive = True                                               # Internal status to my functions

        # Check if we have any connection problems
        try:
            conn = connection()     # Open Socket (gRPC)
            self.send_report(conn.stub,"Information Message","Device connected: " + self._station_name_+
                             " After waiting "+str(self.nextTry) +" seconds")

            informationMsg = conn.getCategory()           # Server side function
            cat_to_run = informationMsg.category          # Return category list

            evtMgr = evtmanager_pb2.evtMgr()
            threads = list()  # Must declare to use thread list
            try:
                for log_type in cat_to_run:                                     # Open thread by log types
                    curr_thr = threading.Thread(target=self.GetEvents,args=(evtMgr,log_type,conn.stub))
                    threads.append(curr_thr)
                    curr_thr.start()
            except Exception as error_massage:  # When it fail, pop-up massage will
                self.send_report(conn.stub, "Error Message", "Thread fail in device: "+self._station_name_
                                 + "\n" + str(error_massage))

            self.ReportServiceStatus(win32service.SERVICE_RUNNING)          # Status: Service Running
            self.send_report(conn.stub,"Information Message","Service Started: "+self._station_name_)
            # --- From here service wait to "stop" command --- #
            rc = None
            while rc != win32event.WAIT_OBJECT_0:  # Wait until the "Stop"
                rc = win32event.WaitForSingleObject(self.hWaitStop, 5000)
            for thread in threads:  # If service was stopped, close all threads
                thread.join()
            self.send_report(conn.stub,"Information Message", "Device stopping connection: "+self._station_name_)
            conn.shutdown()
        except Exception as error_massage:
            print("Error in connection (to open stub)\nNext try in next %d seconds\n Error massage:\n" % self.nextTry)
            print(error_massage)
            time.sleep(self.nextTry)
            self.nextTry *= 2
            return self.SvcDoRun()
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #

    def GetEvents(self, evtmgr, log_type,stub):
        self.clearEvt(log_type)
        hand = win32evtlog.OpenEventLog("localhost", log_type)  # Handle the connection to EventViewer
        flags = win32evtlog.EVENTLOG_FORWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        last_check = win32evtlog.GetNumberOfEventLogRecords(hand)
        self.send_report(stub,"Information Message", "Thread "+log_type + " start to run on: " + self._station_name_)

        evtmgr.hostname = self._station_name_  # Using Socket we can know the PC name
        evtmgr.username = getpass.getuser()     # Using getpass we can know what user is current using
        evtmgr.os = platform.system()           # Using platform to get OS brand
        evtmgr.ip_add = socket.gethostbyname(evtmgr.hostname) # Get the IP Address from socket
        evtmgr.mac_add = get_mac_address(ip=(socket.gethostbyname(evtmgr.hostname))) # Get the MAC_Address

        # ! Important: This while must stop when service is stopped ! #
        while self.keepAlive():
            curr_check = win32evtlog.GetNumberOfEventLogRecords(hand)
            if curr_check > last_check:
                events = win32evtlog.ReadEventLog(hand, flags, curr_check)
                for event in events:
                    evtmgr.id = str(event.EventID)
                    evtmgr.time.FromDatetime(event.TimeGenerated)
                    evtmgr.type = str(event.EventType)
                    evtmgr.src = event.SourceName
                    evtmgr.cat = str(event.EventCategory)
                    data = event.StringInserts
                    data_list = evtmgr.dataList
                    if data:
                        for msg in data:
                            data_list.append(msg)
                    # Push log return true if completed
                    if(stub.PushLog(evtmgr)):   # Debug in gRPC to return value
                        last_check = curr_check
                    else:
                        self.send_report(stub, "Error Message",
                                         "Thread " + log_type + " fail to push from device: " + self._station_name_)

    def clearEvt(self,log_type):
        hand = win32evtlog.OpenEventLog("localhost", log_type)  # Handle the Event Viewer
        win32evtlog.ClearEventLog(hand, None)

    def send_report(self,stub,head,desc):
        report = evtmanager_pb2.ClientReport()
        report.head = head
        report.details = desc
        stub.PushClientReports(report)

    def keepAlive(self):    # Manage the thread's
        return self.alive

# + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +#
# pyinstaller -F --hidden-import=win32timezone --hidden-import=pkg_resources --name=MyService MainService.py clientConnection.py Protobuf/evtmanager_pb2.py ProtoBuf/evtmanager_pb2_grpc.py
#myservice.exe --startup=auto install
# Program Declaration

if __name__ == '__main__':
    # Step 2 checking for arguments got in command line
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(SiemService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(SiemService)
else:
    win32serviceutil.HandleCommandLine(SiemService)

