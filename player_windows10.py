import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 1234))

msg = s.recv(512)

# if the server is to busy he will close socket without response
# if response length is bigger than 0, client accepted to play by server
if len(msg) > 0:
    while not("Thanks" in msg.decode())and not("End" in msg.decode()):
        print(msg.decode())
        response = input("")
        # send response to server
        s.send(bytes(response, "utf-8"))
        msg = s.recv(512)
    # end of game
    print(msg.decode())
    s.close()

