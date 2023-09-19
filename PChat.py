import socket
import sys
import time
import getopt
import os
from threading import Thread
"""
修改自https://blog.csdn.net/songling515010475/article/details/106426124
主要有以下改进：
- 有消息记录
- 支持多个客户端
- 客户端随意登出而服务端不Crash
"""
class WebChat:
    username=""
    server_handles=[]
    addrs=[]
    que=[]
    server=""
    realname=True # 实名制
    f=""
    online=[]
    #输出帮助信息
    def usage(self):
        print("help info : python webChat.py -h")
        print("client : python webChat.py -t [target] -p [port]")
        print("server : python webChat.py -lp [port]")
        sys.exit()
 
    #聊天客户端
    def webChatClient(self, target, port):
        #创建socket套接字
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #连接服务器
        client.connect((target, port))
        print("[*] try to connect the target......")
        #接收服务器发过来的信息
        response = client.recv(1024)
        print(response.decode())
        self.username=input("请输入用户名(不可有空格)>")
        self.f=open("LogOf"+self.username+".txt",mode="a")
        os.system("start python webChat.py -s "+"LogOf"+self.username+".txt")
        print("现在你可以输入消息了，按Enter发送")
        #创建发送消息的线程
        t = Thread(target=self.uploadData, args=(client,))
        #指定当前主线程结束时退出子进程
        t.setDaemon(True)
        #启动线程
        t.start()
 
        # 创建接收消息的线程
        c = Thread(target=self.downloadData, args=("",client,))
        c.setDaemon(True)
        c.start()
        try:
            while True:
                time.sleep(10000)
        #KeyboardInterrupt用来接收Ctrl+c,当接收到命令时就会捕获，并退出
        except KeyboardInterrupt:
            sys.exit()
    #聊天服务端
    def webChatServer(self, port):
        self.f=open("serverlog.txt",mode="a")
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("0.0.0.0",port))
        self.server.listen(255)
        # 不断连接
        l=Thread(target=self.acceptclients,args=())
        l.setDaemon(True)
        l.start()
        # 创建发送消息的线程
        t = Thread(target=self.sendData, args=())
        # 指定当前主线程结束时退出子进程
        t.setDaemon(True)
        # 启动线程
        t.start()
        try:
            time.sleep(10000)
        # KeyboardInterrupt用来接收Ctrl+c,当接收到命令时就会捕获，并退出
        except KeyboardInterrupt:
            sys.exit()
    #不断连接
    def acceptclients(self):
        while True:
            print("[*] Listening on 0.0.0.0:%d"%port)
            server_handle, addr = self.server.accept()
            print("[*] Accept connection from %s:%d"%(addr[0], addr[1]))
            server_handle.send(b"[*] connection successful...")
            self.server_handles.append(server_handle)
            self.addrs.append(addr)
            self.online.append(1)
            # 创建接收消息的线程
            cx = Thread(target=self.recvaData, args=(self.server_handles[-1],self.addrs[-1],len(self.addrs)-1))
            cx.setDaemon(True)
            cx.start()
    #服务端发送数据涵数
    def sendData(self):
        while True:
            if len(self.que):
                data = self.que[0]
                data = data.encode('utf-8')
                for i in range(len(self.server_handles)):
                    if self.online[i]:
                        self.server_handles[i].send(data)
                self.que=self.que[1:]
 
    #服务端接收数据涵数   
    def recvaData(self,socket,addr,it):
        while True:
            try:
                response=socket.recv(1024)
            except ConnectionResetError:
                self.online[it]=0
                return 0
            print("Message received:",response)
            print("Message received:",response,file=self.f)
            self.f.close()
            self.f=open("serverlog.txt",mode="a")
            if response:
                response = response.decode()
                response="At "+time.asctime( time.localtime(time.time()) )+response
                if self.realname:
                    response="From "+str(addr[0])+":"+str(addr[1])+" "+response
                self.que.append(response)
                
    #客户端发送数据涵数
    def uploadData(self, socket):
        while True:
            data = input(">>> ")
            if data == "@reshow":
                os.system("start python webChat.py -s "+"LogOf"+self.username+".txt")
            else:
                data = (" | "+self.username+" >\n"+data+"\n"+57*"_").encode('utf-8')
                socket.send(data)
 
    #客户端接收数据涵数
    def downloadData(self,name, socket):
        while True:
            response = socket.recv(1024)
            if response:
                response = response.decode()
                print(name,response,file=self.f)
                self.f.close()
                self.f=open("LogOf"+self.username+".txt",mode="a")
 
if __name__ == "__main__":
    target = ""
    port = 0
    listen = False
    help = False
    opts, args = getopt.getopt(sys.argv[1:], "t:p:lh:s") #利用getopt模块获取从命令行中的参数
    for o,a in opts:
        if o == "-t":
            target = a
        elif o == "-p":
            port = int(a)
        elif o == "-l":
            listen = True
        elif o == "-h":
            help == True
        elif o=="-s":
            os.system("title "+sys.argv[2][5:-4])
            lu=0
            while True:
                while True:
                    time.sleep(0.1)
                    x=os.path.getmtime(sys.argv[2])
                    if x>lu:
                        lu=x
                        break
                os.system("cls")
                os.system("type "+sys.argv[2])
        else:
            assert False, "Unhandled Option"
    test = WebChat()
    if help:#输出帮助信息
        test.usage()
    elif listen:#调用服务器
        test.webChatServer(port)
    else:#调用客户端
        test.webChatClient(target, port)
