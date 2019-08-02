import grpc
import asyncio
from ProtoBuf import evtmanager_pb2_grpc,evtmanager_pb2

class connection():

    def __init__(self):
        # open a gRPC channel
        channel = grpc.insecure_channel('192.168.0.123:50051')

        # create a stub (client)
        self.stub = evtmanager_pb2_grpc.informationExchangeStub(channel)

    def getCategory(self):
        self.stub.getInfo(evtmanager_pb2.ack(isDeliver=True))

    def sendEvent(self, evt):
        self.stub.PushLog(evt)

if __name__ == '__main__':
    pass