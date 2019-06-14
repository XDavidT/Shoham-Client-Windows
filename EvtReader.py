import win32evtlog # requires pywin32 pre-installed
import time        # Must have to wait


def GetEvents():
    server = "localhost"  # name of the target computer to get event logs
    logtype = "Security"  # 'Application' # 'Security' # 'System'

    hand = win32evtlog.OpenEventLog(server, logtype)  # Handle the connection
    flags = win32evtlog.EVENTLOG_FORWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    last_check = win32evtlog.GetNumberOfEventLogRecords(hand)

    while True:
            curr_check = win32evtlog.GetNumberOfEventLogRecords(hand)
            if curr_check > last_check:
                events = win32evtlog.ReadEventLog(hand,flags,curr_check)
                for event in events:
                    print("Event Category: ", event.EventCategory)
                    print("Time Generated: ", event.TimeGenerated)
                    print("Source Name: " , event.SourceName)
                    print("Event ID: " , event.EventID)
                    print("Event Type: " , event.EventType)
                    print("\n")
                    data = event.StringInserts
                    if data:
                        data_content = "Data: "
                        for msg in data:
                            data_content += msg+"\n"
                        print(data_content)
                    print("---------------------------------------------------------------------------------\n")
                last_check = curr_check
        # slave = Evt(event.EventID,event.TimeGenerated,event.EventType,event.EventCategory,event.SourceName,data_content)
        #Now need to move this slave using protoBuf


def clearEvt():
    server = "localhost"  # name of the target computer to get event logs
    logtype = "Security"  # 'Application' # 'Security' # 'System'
    hand = win32evtlog.OpenEventLog(server, logtype)  # Handle the connection
    win32evtlog.ClearEventLog(hand,None)