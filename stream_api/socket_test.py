import socket
import time
import random


host = "0.0.0.0"
port = 9999

print("starting the server")
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_server:
    print("binding to host and port")
    socket_server.bind((host, port))
    print("listening")
    socket_server.listen(3)
    print("waiting for connection")
    conn, addr = socket_server.accept()
    print(f"accepted connection from {addr}")

    while True:
        i = random.randint(1, 10)
        print("sending stuff")
        conn.sendall(f"{i},{i}\n".encode("utf-8"))
        print("data sent")
        time.sleep(2)
