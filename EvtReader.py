import win32evtlog # requires pywin32 pre-installed
import evtmanager_pb2

server = "localhost"  # name of the target computer to get event logs
logtype = "Security"  # 'Application' # 'Security' # 'System'

def GetEvents(evtMgr):
    hand = win32evtlog.OpenEventLog(server, logtype)  # Handle the connection
    flags = win32evtlog.EVENTLOG_FORWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    last_check = win32evtlog.GetNumberOfEventLogRecords(hand)
    while True:
            curr_check = win32evtlog.GetNumberOfEventLogRecords(hand)
            if curr_check > last_check:
                events = win32evtlog.ReadEventLog(hand, flags, curr_check)
                for event in events:
                    # print(type(event.EventID))
                    evtMgr.id = event.EventID
                    evtMgr.time.FromDatetime(event.TimeGenerated)
                    # print(type(event.EventType))
                    evtMgr.type = event.EventType
                    evtMgr.src = event.SourceName
                    evtMgr.cat = event.EventCategory
                    data = event.StringInserts
                    if data:
                        for msg in data:
                            data_input = evtMgr.dataList.add()
                            data_input.data = msg
                    print(evtMgr.SerializeToString())
                    print("---------------------------------------------------------------------------------\n")
                last_check = curr_check

        # slave = Evt(event.EventID,event.TimeGenerated,event.EventType,event.EventCategory,event.SourceName,data_content)
        #Now need to move this slave using protoBuf



evtMgr = evtmanager_pb2.evtMgr()
GetEvents(evtMgr)











def clearEvt():
    hand = win32evtlog.OpenEventLog(server, logtype)  # Handle the connection
    win32evtlog.ClearEventLog(hand,None)