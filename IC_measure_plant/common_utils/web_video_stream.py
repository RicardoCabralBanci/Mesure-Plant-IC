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
	def do_GET(self):
		s = self.stream[self.path[1:].split('.')[0]]
		if self.path.endswith('.mjpg'):
			self.send_response(200)
			self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
			self.end_headers()
			while self.keeper:
				img = s.get_frame()
				if img is not None:
					success, a_numpy = cv2.imencode('.jpg', img)
					a = a_numpy.tostring()
					self.wfile.write("--jpgboundary".encode('utf-8'))
					self.send_header('Content-type','image/jpeg')
					self.send_header('Content-length',str(len(a)))
					self.end_headers()
					self.wfile.write(a)
					time.sleep(0.001)
		return
	def do_POST(self):
		self.send_response(200)
		self.send_header('Content-type','text/xml')
		self.end_headers()
		self.wfile.write('<ping>None</to>'.encode())
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

	def pass_stream(self, stream, fileName):
		self.RequestHandlerClass.keeper = True
		self.RequestHandlerClass.stream[fileName] = stream
	def close_keeper(self):
		self.RequestHandlerClass.keeper = False

#Wrapper Class
class mjpg_stream():
	def __init__(self,
						ip='127.0.0.1',
						port=8080,
						fileName='stream',
						certfile=None,keyfile=None,
						auth='admin:admin',text='',title='',heading='',
						supressDebug=False):
		if certfile == None or keyfile == None:
			self.ssl = False
		else:
			self.keyfile = keyfile
			self.certfile = certfile
			self.ssl = True
		self.title=title
		self.heading=heading
		self.text = text
		self.port = port
		self.ip = ip
		self.supressDebug = supressDebug
		self.fileName = fileName
		self.auth = auth
		self.frame = None
		Thread(target=self._start_server).start()
	def set_html_text(self,text):
		self.text=text
	def set_html_title(self,text):
		self.text=text
	def set_html_heading(self,text):
		self.text=text
	def get_frame(self):
		return self.frame
	def update_frame(self, frame):
		self.frame = frame
	def _start_server(self):
		try:
			self.server = ThreadedHTTPServer((self.ip, self.port), CamHandler)
			self.server.pass_stream(self,self.fileName)
			if(self.ssl):
				self.server.socket = ssl.wrap_socket(self.server.socket, certfile=self.certfile,keyfile=self.keyfile, server_side=True)
				if not self.supressDebug:
					print("-> MJPG stream is running: https://"+self.ip+":"+str(self.port)+'/'+self.fileName+'.mjpg')
			else:
				if not self.supressDebug:
					print ("-> MJPG stream is running: http://"+self.ip+":"+str(self.port)+'/'+self.fileName+'.mjpg')
			self.server.serve_forever()
		except KeyboardInterrupt:
			self.server.socket.close()
	def disconnect(self):
		self.server.close_keeper()
		self.server.shutdown()
		self.server.socket.close()
