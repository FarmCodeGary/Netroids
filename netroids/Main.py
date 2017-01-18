import socket

def getLocalAddress():
    localAddress = socket.gethostbyname(socket.gethostname())
    typedAddress = raw_input("Enter your external IP address (default: "+localAddress+"): ").strip()
    if typedAddress != "":
        localAddress = typedAddress
    return localAddress

name = raw_input("Enter your name (default: Player): ").strip()
name = name.replace(" ","").replace("|","").replace(":","")
if name == "":
    name = "Player"
clientOrServer = raw_input("Type 1 to start a server, or 2 to start as a client (default: 1): ")
if clientOrServer.strip() == "2":
    localAddress = getLocalAddress()
    serverAddress = raw_input("Enter the IP address of a server: ").strip()
    import mClient
    client = mClient.Client(localAddress, serverAddress, name)
    client.go()
else:
    localAddress = getLocalAddress()
    import mServer
    server = mServer.Server(localAddress, name)
    server.go()
