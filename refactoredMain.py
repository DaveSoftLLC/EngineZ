import socket, threading
from pygame import *
from math import*
from glob import*
import copy
import requests
import json
TCP_IP = '159.203.163.149'
TCP_PORT = 8080
BUFFER_SIZE = 500
mixer.init()
class GameMode:
    def __init__(self):
        self.resolution = (1280,800)
        self.music = mixer.music.load("Outcast.wav")
        self.textFont = font.SysFont("Arial",25)
        self.players = {}
        self.background = image.load('Background/MapFinal.png')
    def drawScreen(self,player):
        try:
            px,py = player.get_pos()
            portion = background.subsurface(Rect(px-screen.get_width()//2,
                                                 py-screen.get_height()//2,
                                                 screen.get_width(),screen.get_height()))
            screen.blit(portion,(0,0))
        except:
            print(px,py)

class Actor:
    def __init__(self,name,pos,spriteFiles):
        self.sprites = spriteFiles
        self.actorList = [name,pos,]
        
