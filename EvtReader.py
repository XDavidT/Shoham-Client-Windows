import win32evtlog # requires pywin32 pre-installed
import time        # Must have to wait
from EvtClass import Evt

def GetEvents():
    server = "localhost"  # name of the target computer to get event logs
    logtype = "Security"  # 'Application' # 'Security' # 'System'

    hand = win32evtlog.OpenEventLog(server, logtype)  # Handle the connection
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    curr_size = win32evtlog.GetNumberOfEventLogRecords(hand)
    last_size = curr_size - 1
    # file1 = open("textfile.txt", 'w+')

    while True:
        while curr_size == last_size:  # Get only new logs+
            time.sleep(1)
            curr_size = win32evtlog.GetNumberOfEventLogRecords(hand)
        events = win32evtlog.ReadEventLog(hand, flags, 0)
        if events:
            for event in events:
                # print("Event Category: " ,event.EventCategory)
                # print("Time Generated: ", event.TimeGenerated)
                # print("Source Name: " , event.SourceName)
                # print("Event ID: " , event.EventID)
                # print("Event Type: " , event.EventType)
                data = event.StringInserts
                if data:
                    data_content = ""
                    for msg in data:
                        data_content += msg
        slave = Evt(event.EventID,event.TimeGenerated,event.EventType,event.EventCategory,event.SourceName,data_content)
        #Now need to move this slave using protoBuf #ToDo
        last_size += 1
        print("---------------------------------------------------------------------------------\n")
