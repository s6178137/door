#!/usr/bin/evn python

from threading import Thread
from threading import Timer
import threading

# RFID
import rfid

# Door Relay
import RPi.GPIO as GPIO
import time

# pygame
from pygame.locals import *
from sys import exit
import pygame
import os, sys

# video
import pexpect
import re
from time import sleep

# socket
import socket
from uuid import getnode as get_mac
from ftplib import FTP
import subprocess


class Marquee(Thread):
	x = 0
	y = 10
	top_text = 0
	bot_text = 0
	ok_text = 0
	deny_text = 0
	#changMessage = True
	changMessage = "default"
	screen = 0
	SCREEN_SIZE = (1024, 768)
	count = 0
	
	def init(self):
		# threading.Thread.__init__(self)
		top_message = "Hello IDIC"
		bot_message = "Wellcome"
		ok_message_m = "Hello Mr."
		ok_message_w = "Hello Ms."
		deny_message = "ID does't exist"

		file = open("color.txt", "r")
		color = file.read().split(',')
		file.close()

		pygame.init()
		self.screen = pygame.display.set_mode(self.SCREEN_SIZE)
		pygame.mouse.set_visible(False)

		font = pygame.font.SysFont("freemono", 50);
		# self.top_text = font.render(top_message, True, (0,255,0))
		self.top_text = font.render(top_message, True, (int(color[0]),int(color[1]),int(color[2])))
		self.bot_text = font.render(bot_message, True, (255,255,255))
		self.ok_text_m = font.render(ok_message_m, True, (255,0,0))
		self.ok_text_w = font.render(ok_message_w, True, (255,0,0))
		self.deny_text = font.render(deny_message, True, (255,0,0))

		self.x = self.SCREEN_SIZE[0]
		self.y = 10


	def run(self):
		self.init()
		while True:
			#print "."
			self.updateScreen()
			time.sleep(0.018)


	def updateScreen(self):
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					#command = "/usr/bin/sudo /sbin/shutdown -r now"
					#process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
					# v.omx.stop()
					exit()

		self.x -= 20
		if self.x < -self.top_text.get_width():
			self.x = self.SCREEN_SIZE[0]
		self.y = 10

		if self.changMessage == "default":
			self.screen.blit(self.bot_text, (self.x,self.y*70))
		elif self.changMessage == "OK_m":
			self.screen.blit(self.ok_text_m, (self.x,self.y*70))
		elif self.changMessage == "OK_w":
			self.screen.blit(self.ok_text_w, (self.x,self.y*70))
			if self.x == self.SCREEN_SIZE[0]:
				self.count += 1
				if self.count == 3:
					self.changMessage = "default"
					self.count = 0
		elif self.changMessage == "Deny":
			self.screen.blit(self.deny_text, (self.x,self.y*70))
			if self.x == self.SCREEN_SIZE[0]:
				self.count += 1
				if self.count == 3:
					self.changMessage = "default"
					self.count = 0
		self.screen.blit(self.top_text, (self.x,self.y))
		pygame.display.update()
		self.screen.fill((0,0,0))


class RfidReader(Thread):
	# marquee = 0
	# def __init__(self, marquee):
		# threading.Thread.__init__(self)
		# self.marquee = marquee

	rfidclient = 0
	def __init__(self, rfidclient):
		threading.Thread.__init__(self)
		self.rfidclient = rfidclient


	def run(self):
		self.__init__(self)
		MIFAREReader = rfid.MFRC522()
		while True:
			#print "Read RFID"
			(status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
			(status, backData) = MIFAREReader.MFRC522_Anticoll()
			if status == MIFAREReader.MI_OK:
				card_id = str(backData[0])+str(backData[1])+str(backData[2])+str(backData[3])+str(backData[4])
				# print card_id + "on rfid"
				self.parseCard(card_id)
			time.sleep(0.02)


	def parseCard(self, cardId):
		# if cardId == "612403120224":
			# m.changMessage = "OK"
			# self.openDoor()
		# elif cardId == "18117717213192":
			# m.changMessage = "Deny"
		# c.data = cardId
		# print cardId + "on func"
		c.transrfid = "OK"
		c.DCTL(cardId)

	def openDoor(self):
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(3, GPIO.OUT)
		GPIO.output(3, False)
		time.sleep(5)
		GPIO.output(3, True)
		GPIO.cleanup()


class RfidClient(Thread):
	host = ''
	port = 0
	address = ''
	transrfid = "default"
	transstat = "OK"
	marquee = 0

	def __init__(self, marquee):
		threading.Thread.__init__(self)
		self.marquee = marquee
		self.host = '192.168.1.101'
		# self.host ='203.64.105.151'
		self.port = 12345
		self.address = (self.host, self.port)
		self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def run(self):
		self.__init__(self)
		self.conn.connect(self.address)
		i = 1
		while True:
			if i == 1:
				self.REGN(self.conn, self.host)
				i += 1
			try:
				data = self.conn.recv(1024)
			except socket.error, e:
				file = open('eror.txt', 'w')
				file.write(e)
				file.close()
			if not data:
				break
			print data
			print len(data)
			self.event(data, self.conn)
			sleep(0.5)

	def REGN(self, conn, host):
		mac = get_mac()
		mes = "REGN " + str(hex(mac)) + " " + str(host)
		self.conn.send(mes)

	def DCTL(self, cardId):
		if self.transrfid == "OK" and self.transstat == "OK":
			self.transstat = "processing"
			print cardId
			mes = "DCTL " + str(cardId)
			self.conn.send(mes)

	def SYNC(self, conn):
		print "o"

	def openDoor(self):
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(3, GPIO.OUT)
		GPIO.output(3, False)
		time.sleep(5)
		GPIO.output(3, True)
		# GPIO.cleanup()

	def event(self, data, conn):
		# print "in evnet"
		# print data + " in event"
		
		check = str(data)[0:4]
		val = str(data)[4:8]
		name = str(data)[8:10]
		# print check, "check is ",len(check)
		# print val, "val is ",len(val)
		if check == "HELO":
			t = time.strftime('%Y-%m-%d',time.localtime(time.time()))
			conn.send("601 " + t)
		elif check == "101 ":
			file = open('code.txt', 'w')
			file.write(val)
			file.close()
		elif check == "301 ":
			if val == "OPEN":
				if name == "Mr":
					m.changMessage = "OK_m"
					self.openDoor()
					self.transrfid = "default"
					self.transstat = "OK"
					m.changMessage = "default"
				elif name == "Ms":
					m.changMessage = "OK_w"
					self.openDoor()
					self.transrfid = "default"
					self.transstat = "OK"
					m.changMessage = "default"
			elif val == "CLOSE":
				m.changMessage = "Deny"
		elif check == "RNEW":
			self.conn.send("401 ")
			remotepath = '/video/video_list.txt'
			ftp = self.ftpconnect()
			bufsize = 1024
			localpath = 'video_list_new.txt'
			fp = open(localpath, 'w')
			ftp.retrbinary('RETR ' + remotepath, fp.write, bufsize)
			ftp.set_debuglevel(0)
			fp.close()
			ftp.quit()
		elif check == "LNEW":
			self.conn.send("701 ")
			remotepath = '/list/list.txt'
			ftp = self.ftpconnect()
			bufsize = 1024
			localpath = 'list.txt'
			fp = open(localpath, 'w')
			ftp.retrbinary('RETR ' + remotepath, fp.write, bufsize)
			ftp.set_debuglevel(0)
			fp.close()
			ftp.quit()
			self.conn.send("703 ")
		elif check == "UPDE":
			self.conn.send("201 ")
			remotepath = '/color.txt'
			ftp = self.ftpconnect()
			bufsize = 1024
			localpath = 'color.txt'
			fp = open(localpath, 'w')
			ftp.retrbinary('RETR ' + remotepath, fp.write, bufsize)
			ftp.set_debuglevel(0)
			fp.close()
			ftp.quit()
			self.conn.send("203 ")
			command = "/usr/bin/sudo /sbin/shutdown -r now"
			process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
			
	def ftpconnect(self):
		ftp_server = '192.168.1.101'
		user = 'root'
		pasw = '12345'
		ftp = FTP()
		ftp.set_debuglevel(2)
		ftp.connect(ftp_server, 21)
		ftp.login(user, pasw)
		return ftp

class OMXPlayer(object):

	_FILEPROP_REXP = re.compile(r".*audio streams (\d+) video streams (\d+) chapters (\d+) subtitles (\d+).*")
	_VIDEOPROP_REXP = re.compile(r".*Video codec ([\w-]+) width (\d+) height (\d+) profile (\d+) fps ([\d.]+).*")
	_AUDIOPROP_REXP = re.compile(r"Audio codec (\w+) channels (\d+) samplerate (\d+) bitspersample (\d+).*")
	_STATUS_REXP = re.compile(r"V :\s*([\d.]+).*")
	_DONE_REXP = re.compile(r"have a nice day.*")

	_LAUNCH_CMD = '/usr/bin/omxplayer -s %s %s'
	_PAUSE_CMD = 'p'
	_TOGGLE_SUB_CMD = 's'
	_QUIT_CMD = 'q'

	paused = False
	subtitles_visible = False
	start_play_signal = False
	end_play_signal = True

	def __init__(self, mediafile, args=None, start_playback=False, do_dict=False):
		if not args:
			args = ""

		self.start_play_signal = False
		self.end_play_signal = True
		cmd = self._LAUNCH_CMD % (mediafile, args)
		self._process = pexpect.spawn(cmd)

		if do_dict:
			self.make_dict()

		self._position_thread = Thread(target=self._get_position)
		self._position_thread.start()
		if not start_playback:
			self.pause()

	def _get_position(self):

		self.start_play_signal = True
		self.end_play_signal = False

		self.position=-100.0

		while True:
			index = self._process.expect([self._STATUS_REXP, pexpect.TIMEOUT, pexpect.EOF, self._DONE_REXP])
			if index == 1: continue
			elif index in (2, 3):
				self.start_play_signal = False
				self.end_play_signal = True
				print 'video is end'
				break
			else:
				self.position = float(self._process.match.group(1))
			sleep(0.05)

	def make_dict(self):
		self.video = dict()
		self.audio = dict()

		try:
			file_props = self._FILEPROP_REXP.match(self._process.readline()).groups()
		except AttributeError:
			return False
		(self.audio['streams'], self.video['streams'], self.chapters, self.subtitles) = [int(x) for x in file_props]

		try:
			video_props = self._VIDEOPROP_REXP.match(self._process.readline()).groups()
		except AttributeError:
			return False
		self.video['decoder'] = video_props[0]
		self.video['dimensions'] = tuple(int(x) for x in video_props[1:3])
		self.video['profile'] = int(video_props[3])
		self.video['fps'] = float(video_props[4])

		try:
			audio_props = self._AUDIOPROP_REXP.match(self._process.readline()).groups()
		except AttributeError:
			return False
		self.audio['decoder'] = audio_props[0]
		(self.audio['channels'], self.audio['rate'], self.audio['bps']) = [int(x) for x in audio_props[1:]]

		if self.audio['streams'] > 0:
			self.current_audio_stream = 1
			self.current_volume = 0.0

	def pause(self):
		if self._process.send(self._PAUSE_CMD):
			self.paused = not self.paused

	def stop(self):
		self._process.send(self._QUIT_CMD)
		self._process.terminate(force=True)

class MediaPlayer(Thread):
	omx = OMXPlayer
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		video_list = self.readlist()
		list_count = len(video_list) - 1
		start_num = 0
		print "list count have:" + repr(list_count)
		while True:
			# print self.omx.start_play_signal
			if self.omx.start_play_signal == False:
				self.omx = OMXPlayer(video_list[start_num])
				# print "video:" + repr(list[start_num])
				# print "video number:" + repr(start_num)
				if os.path.exists("video_list_new.txt") == True:
					file = open("video_list_new.txt", "r")
					list_new = file.read().split('\n')
					list_new.pop()
					file.close()
					video_list = list_new
					start_num = 0
					list_count = len(video_list) - 1
					os.renames("video_list_new.txt", "video_list.txt")
				elif list_count > start_num:
					start_num += 1
				elif list_count == start_num:
					start_num = 0
			sleep(2)
			
	def readlist(self):
		file = open("video_list.txt", "r")
		list = file.read().split('\n')
		list.pop()
		print list
		file.close()
		return list

class doorButton(Thread):
	rfidclient = 0
	def __init__(self, rfidclient):
		threading.Thread.__init__(self)
		self.rfidclient = rfidclient
	def run(self):
		self.__init__(self)
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(7, GPIO.IN, pull_up_down = GPIO.PUD_UP)
		while True:
			if (GPIO.input(7) == 0):
				c.openDoor()
			sleep(0.1)

############################################
#-------------------main-------------------#
############################################
if __name__ == "__main__":

	v = MediaPlayer()
	v.start()
	m = Marquee()
	m.start()
	c = RfidClient(m)
	c.start()
	r = RfidReader(c)
	r.start()
	d = doorButton(c)
	d.start()

