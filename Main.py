import win32evtlog # requires pywin32 pre-installed
import time

server = "localhost" # name of the target computer to get event logs
logtype = "Security" # 'Application' # 'Security' # 'System'

hand = win32evtlog.OpenEventLog(server, logtype)    # Handle the connection
flags = win32evtlog.EVENTLOG_BACKWARDS_READ|win32evtlog.EVENTLOG_SEQUENTIAL_READ
curr_size = win32evtlog.GetNumberOfEventLogRecords(hand)
last_size = curr_size
# file1 = open("textfile.txt", 'w+')

while True:
    curr_size = win32evtlog.GetNumberOfEventLogRecords(hand)
    while curr_size == last_size: # Get only new logs
        time.sleep(1)
    events = win32evtlog.ReadEventLog(hand, flags,0)
    if events:
        for event in events:
            print ("Event Category:"), event.EventCategory
            print ("Time Generated:"), event.TimeGenerated
            print ("Source Name:"), event.SourceName
            print ("Event ID:"), event.EventID
            print ("Event Type:"), event.EventType
            print ("---------------------------------------------------------------------------------\n")
            # data = event.StringInserts
            #
            # if data:
            #     print ("Event Data:")
            #     for msg in data:
            #         print("---------------------------------------------------------------------------------")
            #         print (msg)
    last_size += 1