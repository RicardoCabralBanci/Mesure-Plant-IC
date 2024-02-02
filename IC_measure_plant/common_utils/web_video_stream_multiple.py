import cv2
from PIL import Image
import threading
from http.server import BaseHTTPRequestHandler,HTTPServer
from socketserver import ThreadingMixIn
from io import StringIO
import time
from threading import Thread
import socket
import base64
import ssl

#HTTP Classes
class CamHandler(BaseHTTPRequestHandler):
	stream = {}
	keeper = True
	''' Main class to present webpages and authentication. '''
	def do_HEAD(self):
		self.send_response(200)
		self.end_headers()
	def do_AUTHHEAD(self):
		self.send_response(401)
		self.send_header('WWW-Authenticate', 'Basic realm=\"Test\"')
		self.end_headers()

	def do_GET_FRAME(self, idx):
		self.send_response(200)
		self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
		self.end_headers()
		while self.keeper:
			img = self.stream.frame[idx]
			if img is not None:
				success, a_numpy = cv2.imencode('.jpg', img)
				a = a_numpy.tostring()
				self.wfile.write("--jpgboundary".encode('utf-8'))
				self.send_header('Content-type','image/jpeg')
				self.send_header('Content-length',str(len(a)))
				self.end_headers()
				self.wfile.write(a)
				time.sleep(0.001)
	def do_GET(self):
		if self.path.endswith('.mjpg'):
			for idx in range(len(self.stream.streams)):
				if self.stream.streams[idx] in self.path:
					self.do_GET_FRAME(idx)
		return
	def finish(self,*args,**kw):
		self.keeper = False
		try:
			BaseHTTPRequestHandler.finish(self)
		except socket.error:
			pass
	def handle(self):
		try:
			BaseHTTPRequestHandler.handle(self)
		except socket.error:
			pass
	def log_message(self, format, *args):
		return
	def update_frame(self,frame):
		self.frame = frame

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""
	stopped = False

	def pass_stream(self, stream):
		self.RequestHandlerClass.keeper = True
		self.RequestHandlerClass.stream = stream
	def close_keeper(self):
		self.RequestHandlerClass.keeper = False

#Wrapper Class
class mjpg_stream():
	def __init__(self,ip='127.0.0.1',port=8080,streams=['stream'],certfile=None,keyfile=None):
		if certfile == None or keyfile == None:
			self.ssl = False
		else:
			self.keyfile = keyfile
			self.certfile = certfile
			self.ssl = True
		self.port = port
		self.ip = ip
		self.frame = []
		for x in streams:
			self.frame.append(None)
		self.streams = streams
		Thread(target=self._start_server).start()
	def update_frame(self, frame, idx):
		self.frame[idx] = frame
	def _start_server(self):
		self.server = ThreadedHTTPServer((self.ip, self.port), CamHandler)
		self.server.pass_stream(self)
		if(self.ssl):
			self.server.socket = ssl.wrap_socket(self.server.socket, certfile=self.certfile,keyfile=self.keyfile, server_side=True)
			for x in self.streams:
				print("-> MJPG stream is running: https://"+self.ip+":"+str(self.port)+'/'+x+'.mjpg')
		else:
			for x in self.streams:
				print ("-> MJPG stream is running: http://"+self.ip+":"+str(self.port)+'/'+x+'.mjpg')
		self.server.serve_forever()
	def disconnect(self):
		self.server.close_keeper()
		self.server.shutdown()
		self.server.socket.close()
