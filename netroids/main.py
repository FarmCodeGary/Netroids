import socket


def get_local_address():
    local_address = socket.gethostbyname(socket.gethostname())
    typed_address = raw_input(
        "Enter your external IP address (default: "+local_address+"): ").strip()
    if typed_address != "":
        local_address = typed_address
    return local_address

if __name__ == "__main__":
    name = raw_input("Enter your name (default: Player): ").strip()
    name = name.replace(" ", "").replace("|", "").replace(":", "")
    if name == "":
        name = "Player"
    client_or_server = raw_input(
        "Type 1 to start a server, or 2 to start as a client (default: 1): ")
    if client_or_server.strip() == "2":
        local_address = get_local_address()
        server_address = raw_input("Enter the IP address of a server: ").strip()
        import mClient
        client = mClient.Client(local_address, server_address, name)
        client.go()
    else:
        local_address = get_local_address()
        import mServer
        server = mServer.Server(local_address, name)
        server.go()
