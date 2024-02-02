#-*- coding: utf-8 -*-

#System Stuff
import time
from threading import Thread

# pyftpdlib import
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import MultiprocessFTPServer
from pyftpdlib.authorizers import DummyAuthorizer
import pyftpdlib.log as ftp_log


#This class handles FTP connections
class ftp_server:
    #Starts up FTP Server
    def __init__(self, ip='', port=2121, logs_from_pyftpdlib=False, anonymous_can_write=False):
        if not logs_from_pyftpdlib:
            ftp_log.LEVEL = ftp_log.logging.ERROR
        self._anonymous_can_write = anonymous_can_write
        self.ip = ip
        self.port = port

        #Starts up a Thread so that the main program does not hang
        Thread(target=self.main_ftp).start()
        #Waits for main_ftp to reach serve_forever
        time.sleep(1)

        return
    #Main FTP Server Thread
    def main_ftp(self):
        self.authorizer = DummyAuthorizer()

        if self._anonymous_can_write:
            self.authorizer.add_anonymous("nobody", perm="elradfmwM")
        else:
            self.authorizer.add_anonymous("nobody")

        handler = FTPHandler
        handler.authorizer = self.authorizer
        self.server = MultiprocessFTPServer((self.ip, self.port), handler)
        self.server.serve_forever(timeout=5)

    #Add user to FTP Server
    def add_user(self, user, password, root_folder, give_write_permition=True):
        if give_write_permition:
            self.authorizer.add_user(user, password, root_folder, perm="elradfmwM")
        else:
            self.authorizer.add_user(user, password, root_folder)
        print('[FTP SERVER] User Added: '+user)

    def clean_up(self):
        self.server.close_all()
