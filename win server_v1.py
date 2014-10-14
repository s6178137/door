from Tkinter import *
import Tkinter as tk
import tkMessageBox
import os
from threading import Thread
from threading import Timer
import threading
import thread
from socket import *
import socket
import time
from time import sleep
import MySQLdb
import random
class Server(threading.Thread):
	def __init__(self, Message_box, Input_message):
		threading.Thread.__init__(self)
		self.Message_box = Message_box
		self.Input_message = Input_message
		self.host = gethostname()
		# self.host = 'localhost'
		self.port = 12345
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def run(self):
		self.server.bind((self.host, self.port))
		self.server.listen(1)
		i = 1
		while True:
			self.Message_box.insert(END, 'Server:waiting for connection.....\n')
			(conn, addr) = self.server.accept()
			mes =  'Connected from:' + str(addr) + '\n'
			self.Message_box.insert(END, mes)
			while True:
				if i == 1 and addr > 0:
					self.helo = HELO(conn)
					self.helo.setDaemon(True)
					self.helo.start()
					self.bu = Bu_event(conn)
					self.bu.setDaemon(True)
					self.bu.start()
					i += 1
				data = conn.recv(1024)
				print data
				self.Message_box.insert(END, data + '\n')
				self.Message_box.see(END)
				if not data:
					break
				self.event(conn, data)
				sleep(0.5)
				
	def button_event(self):
		mes = self.Input_message.get(1.0, END)
		self.Message_box.insert(END, mes + '\n')
		self.Message_box.see(END)
		self.Input_message.delete(1.0, END)
		self.bu.event(mes, self.Message_box)
	
	def event(self, conn, data):
		check = data[:4]
		val = data[5:]
		# print data
		# print len(data)
		# print check
		# print len(check)
		# print val
		# print len(val)
		if check == "DCTL":
			db = MySQLdb.connect('localhost', 'root', '', 'door')
			cur = db.cursor()
			cur.execute("SELECT * FROM `list` WHERE `rfid` LIKE %s", val)
			res = cur.fetchone()
			print res
			if res > 1:
				conn.send("301 OPEN" + str(res[1]))
				cur.execute("INSERT INTO door.log (rfid, stat) VALUES (%s, 'OPEN')", val)
				db.commit()
			elif res == None:
				conn.send("301 CLOSE")
				cur.execute("INSERT INTO door.log (rfid, stat) VALUES (%s, 'CLOSE')", val)
				db.commit()
			db.close()
			check = ""
			val = ""
		elif check == "REGN":
			en = str(unichr(random.randrange(65, 90, 2)))
			nu = random.randrange(0, 99999, 5)
			code = en + str(nu)
			mes = str(val[0:15])
			print mes
			db = MySQLdb.connect('localhost', 'root', '', 'door')
			cur = db.cursor()
			cur.execute("INSERT INTO door.code (mac, code) VALUES (%s, %s)", (mes, code))
			db.commit()
			db.close()
			conn.send("101 " + code)
		elif check == "SYNC":
			conn.send("705 record success")
		elif check == "EROR":
			t = time.strftime('%Y-%m-%d',time.localtime(time.time()))
			db = MySQLdb.connect('localhost', 'root', '', 'door')
			cur = db.cursor()
			cur.execute("INSERT INTO door.eror (eror, time) VALUES (%s, %s)", (val, t))
			db.commit()
			db.close()
			conn.send("801 Error report success")
		elif check == "601 ":
			self.Message_box.insert(END, "Client keep alive\n")
			self.Message_box.see(END)

class HELO(threading.Thread):
	def __init__(self, conn):
		threading.Thread.__init__(self)
		self.conn = conn
	def run(self):
		while True:
			self.conn.send("HELO")
			sleep(10)
			
class Bu_event(threading.Thread):
	def __init__(self, conn):
		threading.Thread.__init__(self)
		self.conn = conn
	def run(self):
		print "ready"
		self.conn.send("ready")
	def event(self, data, Message_box):
		if data[0:4] == "LNEW":
			self.conn.send(data)
			Message_box.insert(END, data)
			Message_box.see(END)
		elif data[0:4] == "RNEW":
			self.conn.send(data)
			Message_box.insert(END, data)
			Message_box.see(END)
		elif data[0:4] == "UPDE":
			self.conn.send(data)
			Message_box.insert(END, data)
			Message_box.see(END)
		else:
			Message_box.insert(END, "The command is not exist\n")
			Message_box.see(END)
			
class WinGUI():
	##########GUI##########
	def __init__(self, root):
		self.root = root
		self.root.title("Server")
		self.root.configure(background='grey')
		self.root.geometry('600x400+750+300')
		#windows closing
		self.root.protocol("WM_DELETE_WINDOW", self.win_exit)

		#block
		self.block_top = Label(self.root, width = 60, height = 1)
		self.block_top.grid(row=0, column=1)

		#show Message
		self.Message_box = Text(self.root, width = 60, height = 20)
		self.Message_box.grid(row=1, column=1)

		#block
		self.block_bot = Label(self.root, width = 60, height = 1)
		self.block_bot.grid(row=2, column=1)

		#Enter Message
		self.Input_message = Text(self.root, width = 60, height = 1)
		self.Input_message.grid(row=3, column=1)

		#Enter Button
		self.Enter_button = Button(self.root, width=10, height=1, text='Enter', command=self.message)
		self.Enter_button.grid(row=3, column=2)

		#Conn Button
		self.Conn_button = Button(self.root, width=10, height=1, text='Listen', command=self.Listen)
		self.Conn_button.grid(row=2, column=2)

	def Listen(self):
		#Server
		self.ctrl = Server(self.Message_box, self.Input_message)
		self.ctrl.setDaemon(True)
		self.ctrl.start()

	def message(self):
		# self.ctrl = Server(self.Message_box, self.Input_message)
		self.ctrl.button_event()
		# mes = self.Input_message.get(1.0, END)
		# self.case(mes)
		# self.Input_message.delete(1.0, END)
		# self.Message_box.insert(INSERT, mes)
		# self.Message_box.see(END)

	def win_exit(self):
		self.root.destroy()
		exit()

	# def case(self, mes):
		# s = len(mes)
		# t = mes[0:s-1]
		# print s
		# print t
		# if t == "a":
			# print "hi"
		# else:
			# print "The command is not exist"


if __name__ == "__main__":
	root = Tk()
	windows = WinGUI(root)
	root.mainloop()

