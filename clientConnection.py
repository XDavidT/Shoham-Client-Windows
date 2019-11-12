import grpc
from ProtoBuf import evtmanager_pb2_grpc,evtmanager_pb2

class connection():

    def __init__(self):
        try:
            with open("c:\Program Files\Shoham\server.crt",'rb') as f:
                creds = f.read()
            credentials = grpc.ssl_channel_credentials(root_certificates=creds)
            self.channel = grpc.secure_channel('siem.davidt.net:50051',credentials)
            self.stub = evtmanager_pb2_grpc.informationExchangeStub(self.channel)
        except Exception as e:
            print("Eror in client connection")
            print(e)

    def getCategory(self):
        try:
            return self.stub.getInfo(evtmanager_pb2.ack(isDeliver=True))
        except:
            print("Eror in Category")
    def sendEvent(self, evt):
        self.stub.PushLog(evt)
        print("event sent")

    def shutdown(self):
        self.channel.close()

    def send_client_logs(self,header,details):
        client_report = evtmanager_pb2.ClientReport()
        client_report.head = header
        client_report.details = details
