import win32evtlog # requires pywin32 pre-installed
import time        # Must have to wait
import ctypes, sys # Must have to run as Administrator

def is_admin(): #Run ad admin
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() #Check if user admin
    except:
        return False

if is_admin(): #If Admin - Run this->
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
                print("Event Category: " ,event.EventCategory)
                print("Time Generated: ", event.TimeGenerated)
                print("Source Name: " , event.SourceName)
                print("Event ID: " , event.EventID)
                print("Event Type: " , event.EventType)
                data = event.StringInserts
                if data:
                    print ("Event Data:")
                    for msg in data:
                        print (msg)
        last_size += 1
        print("---------------------------------------------------------------------------------\n")

else: #If not admin - Run as admin  #Re-run the program with admin rights

   ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)






