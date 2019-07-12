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
    songStarted = time.time()
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
    listwalker.set_focus(names.index(name))
    player.play(str(namedict[name]))
    songPlaying = name
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

a = 0
player = mpv.MPV(input_default_bindings=True, input_vo_keyboard=True)
q = queue.Queue()
qhistory = []
names,namedict,durdict = getSongs()

content = [urwid.AttrMap(Song(name),"","reveal focus") for name in names]
palette = [('reveal focus', 'black', 'dark cyan','standout')]
listBox = getSongList(content,a)
mainloop = urwid.MainLoop(listBox,unhandled_input=listener,palette=palette)
mainloop.run()
player.terminate()
