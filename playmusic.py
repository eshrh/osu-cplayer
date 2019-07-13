import os
from pathlib import Path
import mpv
import urwid
import time
import queue
from locale import setlocale, LC_NUMERIC
from tinytag import TinyTag as tag
import pyglet
setlocale(LC_NUMERIC, "C")

##### EDIT THIS TO POINT TO OSU SONGS FOLDER #####
ABSPATH_TO_SONGS = ".."



def getSongs():
    cur = ABSPATH_TO_SONGS
    songdirs = [i for i in [j for j in os.walk(cur)][0][1] if i.split()[0].isdigit()]
    paths = [os.path.join(cur,i) for i in songdirs]
    audios = []
    for i in paths:
        osufile = [i for i in Path(i).glob("*.osu")][0]
        with open(osufile,"r") as f:
            for line in f.readlines():
                if(line.startswith("AudioFilename")):
                    audioFilename = line[line.index(":")+2:].strip()
                    break
        audios.append(Path(i,audioFilename))
    names = []
    namedict = {}
    durdict = {}
    for pos,i in enumerate(songdirs):
        temp = i
        if(i.endswith("[no video]")):
            temp = temp[:-10]
        temp = " ".join(temp.split()[1:])
        names.append(temp)
        namedict[temp] = audios[pos]
        info = tag.get(audios[pos])
        durdict[temp] = info.duration
    return (sorted(list(set(names))),namedict,durdict)

songStarted = 0
songAlarm = 0
songPlaying = 0
songPaused = 0
def trackPlayback(name,duration):
    global songAlarm
    global songStarted
    global songRemain
    songStarted = time.time()

    mainloop.set_alarm_in(0.04,updateBar)
    songAlarm = mainloop.set_alarm_in(duration,nextsong)


def nextsong(loop,data):
    global loopsong
    if data!=1 and loopsong:
        play(songPlaying)
        return 0
    loopsong = False
    if not q.empty():
        play(q.get_nowait())
    else:
        try:
            pos = names.index(songPlaying)
        except (IndexError,ValueError) as e:
            return 0
        if pos!=len(names)-1:
            play(names[pos+1])
        else:
            play(names[0])

def prevsong():
    try:
        pos = names.index(songPlaying)
    except (IndexError,ValueError) as e:
        return 0
    if pos!=0:
        play(names[names.index(songPlaying)-1])


def play(name):
    if songAlarm!=0:
        mainloop.remove_alarm(songAlarm)

    global songPlaying
    global songPaused
    listwalker.set_focus(names.index(name))
    player.play(str(namedict[name]))

    songPlaying = name
    songPaused = 0

    nowplayingtext.set_text(songPlaying)
    mainloop.draw_screen();

    mainloop.set_alarm_in(0.04,updateBar) #?24 fps?

    trackPlayback(name,durdict[name])

def pause():
    global songPaused
    player.pause = not player.pause
    if(player.pause==True):
        mainloop.remove_alarm(songAlarm)
        songPaused = time.time()
    else:
        trackPlayback(songPlaying,durdict[songPlaying]-(songPaused-songStarted))



class Song(urwid.Text):
    def selectable(self):
        return True
    def keypress(self, size, key):
        if(key=='enter'):
            play(self.text)
        if(key=='a'):
            q.put_nowait(self.text)
        return key

listwalker = 0
loopsong = False
def getSongList(content,a):
    global listwalker
    listwalker = urwid.SimpleListWalker(content)
    return urwid.ListBox(listwalker)


nowplayingtext = urwid.Text("osu-cplayer",'center')
def getNowPlaying():
    return urwid.AttrMap(nowplayingtext,'header')

progbar = 0
def updateBar(a,b):
    progbar.set_completion( (time.time()-songStarted)/durdict[songPlaying]*100 )
    mainloop.set_alarm_in(0.1,updateBar)

def getSongProgress():
    global progbar
    progbar = urwid.ProgressBar('barIncomplete','barComplete')
    return progbar

def getHeader():
    header = urwid.Pile([getNowPlaying(),getSongProgress()])
    return header

def listener(key):
    global loopsong
    if(key in {'q','esc','ctrl c'}):
        raise urwid.ExitMainLoop()
    if(key=='p'):
        pause()
    if(key=='right'):
        nextsong(0,1)
    if(key=='left'):
        prevsong()
    if(key=='l'):
        loopsong = not loopsong
        if(loopsong==True):
            nowplayingtext.set_text(songPlaying+" -looping-")
        else:
            nowplayingtext.set_text(songPlaying)

a = 0
player = mpv.MPV(input_default_bindings=True, input_vo_keyboard=True)
q = queue.Queue()
qhistory = []
names,namedict,durdict = getSongs()

content = [urwid.AttrMap(Song(name),"","reveal focus") for name in names]
palette = [('reveal focus', 'black', 'dark cyan','standout'),
           ('header','black','light gray'),
           ('barIncomplete','light gray','light gray'),
           ('barComplete','light green','light green')
]
listBox = getSongList(content,a)
frame = urwid.Frame(listBox,header=getHeader(),footer=urwid.Text("goodbye world"))
mainloop = urwid.MainLoop(frame,unhandled_input=listener,palette=palette)
mainloop.run()
player.terminate()
