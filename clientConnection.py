import grpc
from ProtoBuf import evtmanager_pb2_grpc,evtmanager_pb2

class connection():

    def __init__(self):
        try:
            self.channel = grpc.insecure_channel('localhost:50051')
            self.stub = evtmanager_pb2_grpc.informationExchangeStub(self.channel)
        except:
            print("Eror client connection")

    def getCategory(self):
        try:
            return self.stub.getInfo(evtmanager_pb2.ack(isDeliver=True))
        except:
            print("Eror Category")
    def sendEvent(self, evt):
        self.stub.PushLog(evt)
        print("event sent")

    def shutdown(self):
        self.channel.close()
