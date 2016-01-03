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
		except Exception:
			return None

	def write(self, message):
		self._wbuffer.put(message)

	def close(self):
		self._running = False

	def run(self):
		'''
		Main loop for the irc connection

		Ideally this is the only place in the bot that would need to worry about
		unicode vs byte strings. Everything else should be using unicode strings
		'''
		rbuffer = b""
		while self._running:
			rlist, wlist, xlist = select.select([self._socket], [self._socket], [], 1)
			for s in rlist:
				rbuffer += s.recv(1024)
				tmp = rbuffer.split(b'\r\n')
				rbuffer = tmp.pop()
				for line in tmp:
					decoded = line.decode('utf8')
					log_in.info(decoded)
					self._rbuffer.put(decoded)
			for s in wlist:
				if not self._wbuffer.empty():
					message = self._wbuffer.get()
					log_out.info(message.strip())
					s.send(message.encode('utf8'))
		self._socket.close()
