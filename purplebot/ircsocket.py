import logging
import queue
import select
import socket
import threading

__all__ = ['ircsocket']

log_in = logging.getLogger('irc.in')
log_out = logging.getLogger('irc.out')


class ircsocket(threading.Thread):
	def connect(self, host, port=6667):
		self._rbuffer = queue.Queue()
		self._wbuffer = queue.Queue()
		self._socket = socket.socket()
		self._socket.connect((host, port))
		self._running = True
		self.start()

	def read(self):
		try:
			return self._rbuffer.get_nowait()
		except:
			return None

	def write(self, message):
		self._wbuffer.put(message)

	def close(self):
		self._running = False

	def run(self):
		rbuffer = ""
		while self._running:
			rlist, wlist, xlist = select.select([self._socket], [self._socket], [], 1)
			for s in rlist:
				rbuffer += s.recv(1024)
				tmp = rbuffer.split('\r\n')
				rbuffer = tmp.pop()
				for line in tmp:
					log_in.info(line)
					self._rbuffer.put(line)
			for s in wlist:
				if not self._wbuffer.empty():
					message = self._wbuffer.get()
					log_out.info(message.strip())
					s.send(message)
		self._socket.close()
