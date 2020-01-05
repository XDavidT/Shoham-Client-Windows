# Shoham SIEM System: Windows Client
## What it does ?
By using this client, all the logs collected to Event Viewer sent to logger.
This client made to run as windows service in background. The service is depend [Siem logger service](https://github.com/XDavidT/Shoham-Logger "Siem logger service"), and must be configure to send logs.
Please check *clientConnection.py* to configure certificate and update the logger address.

## How to use ?
1. Clone to windows pc
2. In your python3 need to run 'pip install protoc', once you finish, you can run:
`protoc --proto_path=ProtoBuf --python_out=ProtoBuf ProtoBuf/evtmanager.proto`
`python -m grpc_tools.protoc -I./ProtoBuf --python_out=ProtoBuf --grpc_python_out=ProtoBuf ProtoBuf/evtmanager.proto`
3. Now need to install pyinstaller, by running 'pip install pyinstaller' then run this command:
`pyinstaller -F --hidden-import=win32timezone --hidden-import=pkg_resources --hidden-import=["pywt","pywt._estentions._cwt"] --name=Shoham MainService.py clientConnection.py Protobuf/evtmanager_pb2.py ProtoBuf/evtmanager_pb2_grpc.py`
4. In the folder *dist* you will find EXE file, open cmd and move to current direcotry to this folder. Put the certificate in relevant folder (*c:\Program Files\Shoham\server.crt*)
5. Run the EXE file name & install -> start, example: `Shoham.exe install` -> `Shoham.exe start`
