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
		#threading.Thread.__init__(self)
		top_message = "Hello IDIC"
		bot_message = "Wellcome"
		ok_message = "Hello Mr. X"
		deny_message = "ID does't exist"

		pygame.init()
		self.screen = pygame.display.set_mode(self.SCREEN_SIZE)
		pygame.mouse.set_visible(False)

		font = pygame.font.SysFont("freemono", 50);
		self.top_text = font.render(top_message, True, (0,255,0))
		self.bot_text = font.render(bot_message, True, (255,255,255))
		self.ok_text = font.render(ok_message, True, (255,0,0))
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
					exit()

		self.x -= 20
		if self.x < -self.top_text.get_width():
			self.x = self.SCREEN_SIZE[0]
		self.y = 10

		if self.changMessage == "default":
			self.screen.blit(self.bot_text, (self.x,self.y*70))
		elif self.changMessage == "OK":
			self.screen.blit(self.ok_text, (self.x,self.y*70))
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
	marquee = 0
	def __init__(self, marquee):
		threading.Thread.__init__(self)
		self.marquee = marquee

	# rfidclient = 0
	# def __init__(self, rfidclient):
		# threading.Thread.__init__(self)
		# self.rfidclient = rfidclient


	def run(self):
		self.__init__(self)
		MIFAREReader = rfid.MFRC522()
		while True:
			#print "Read RFID"
			(status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
			(status, backData) = MIFAREReader.MFRC522_Anticoll()
			if status == MIFAREReader.MI_OK:
				card_id = str(backData[0])+str(backData[1])+str(backData[2])+str(backData[3])+str(backData[4])
				print card_id + "on rfid"
				self.parseCard(card_id)
			time.sleep(0.02)


	def parseCard(self, cardId):
		if cardId == "612403120224":
			m.changMessage = "OK"
			self.openDoor()
		elif cardId == "18117717213192":
			m.changMessage = "Deny"
		# c.data = cardId
		# print cardId + "on func"
		# c.transrfid = "OK"

	def openDoor(self):
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(3, GPIO.OUT)
		GPIO.output(3, False)
		time.sleep(5)
		GPIO.output(3, True)

# class RfidClient(Thread):
	# host = ''
	# port = 0
	# data = ''
	# address = ''
	# transrfid = "default"
	# transstat = "OK"
	# marquee = 0

	# def __init__(self, marquee):
		# threading.Thread.__init__(self)
		# self.marquee = marquee
		# self.host = '192.168.1.101'
		# self.port = 12345
		# self.data = 'null'
		# self.address = (self.host, self.port)
		# self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# self.conn.connect(self.address)

	# def run(self):
		# self.__init__(self)
		# while True:
			# if self.transrfid == "OK" and self.transstat == "OK":
				# self.transstat = "processing"
				# print self.data
				# self.conn.send("DCTL %s" % self.data)
				# buf = self.conn.recv(1024)
				# print buf
				# self.move(buf)
				# # if buf == "OK":
				    # # m.changMessage = "OK"
					# # self.openDoor()
					# # self.data = 0
					# # self.transrfid = "default"
					# # self.transstat = "OK"
					# #self.c.close


	# def move(self, Buf_move):
		# if Buf_move == "OK":
			# m.changMessage = "OK"
			# self.openDoor()
			# self.data = 'null'
			# self.transrfid = "default"
			# self.transstat = "OK"

	# def openDoor(self):
		# GPIO.setmode(GPIO.BOARD)
		# GPIO.setup(3, GPIO.OUT)
		# GPIO.output(3, False)
		# time.sleep(5)
		# GPIO.output(3, True)
		# GPIO.cleanup()


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
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		list = ['/root/video/view1.mp4', '/root/video/view2.mp4', '/root/video/view3.mp4']
		list_count = len(list) - 1
		start_num = 0
		# print "list count have:" + repr(list_count)

		omx = OMXPlayer

		while True:
			print omx.start_play_signal
			if omx.start_play_signal == False:
				omx = OMXPlayer(list[start_num])
				# print "video:" + repr(list[start_num])
				# print "video number:" + repr(start_num)
				if list_count > start_num:
					start_num += 1
				elif list_count == start_num:
					start_num = 0
			sleep(1)

class doorButton(Thread):
	rfidreader = 0
	def __init__(self, rfidreader):
		threading.Thread.__init__(self)
		self.rfidreader = rfidreader
	def run(self):
		self.__init__(self)
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(7, GPIO.IN, pull_up_down = GPIO.PUD_UP)
		while True:
			if (GPIO.input(7) == 0):
				r.openDoor()

############################################
#-------------------main-------------------#
############################################
if __name__ == "__main__":

	m = Marquee()
	m.start()
	# c = RfidClient(m)
	# c.start()
	r = RfidReader(m)
	r.start()
	v = MediaPlayer()
	v.start()
	d = doorButton(r)
	d.start()
