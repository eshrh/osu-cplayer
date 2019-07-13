import os
from pathlib import Path
import mpv
import urwid
import time
from collections import deque
from locale import setlocale, LC_NUMERIC
from tinytag import TinyTag as tag
import random
import webbrowser
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

def shuffle():
    random.shuffle(names)
    listwalker.clear()
    for i in names:
        listwalker.append(urwid.AttrMap(Song(i),'','select'))
def sort():
    names.sort()
    listwalker.clear()
    for i in names:
        listwalker.append(urwid.AttrMap(Song(i),'','select'))

songStarted = 0
songAlarm = 0
songPlaying = 0
songPaused = 0
pauseTime = 0
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
    if len(q)>0:
        play(q.pop())
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

realSongStart = 0
progress = 0
def play(name):
    if songAlarm!=0:
        mainloop.remove_alarm(songAlarm)
    if(player.pause):
        pause()
    global songPlaying
    global songPaused
    global pauseTime
    global realSongStart
    global progress

    listwalker.set_focus(names.index(name))
    player.play(str(namedict[name]))
    songPlaying = name
    songPaused = 0
    pauseTime = 0
    realSongStart = time.time()
    progress = 0

    nowplayingtext.set_text(songPlaying)
    mainloop.set_alarm_in(0.1,updateBar)


    mainloop.draw_screen();

     #?24 fps?

    #trackPlayback(name,durdict[name])

def pause():
    global pauseTime
    global songPaused
    global barAlarm
    if(songPlaying==0):
        return 0
    player.pause = not player.pause
    if(player.pause==True):
        mainloop.remove_alarm(songAlarm)
        if barAlarm!=0:
            mainloop.remove_alarm(barAlarm)
        songPaused = time.time()
    else:
        pauseTime+=time.time()-songPaused
        barAlarm = mainloop.set_alarm_in(0.1,updateBar)
        #trackPlayback(songPlaying,durdict[songPlaying]-(pauseTime))


class Song(urwid.Text):
    def __init__(self,txt):
        self.__super.__init__(txt)
        self.lastm1 = 0
    def selectable(self):
        return True
    def keypress(self, size, key):
        if(key=='enter'):
            play(self.text)
        if(key=='a'):
            q.appendleft(self.text)
            disp_notif(f"{self.text} added to queue ({len(q)} items)")
        return key
    def mouse_event(self,size,event,button,col,row,focus):
        if(event=='mouse press' and button==1):
            if time.time()-self.lastm1<0.2:
                play(self.text)
            self.lastm1 = time.time()
        if(event=='mouse press' and button==3):
            q.appendleft(self.text)
            disp_notif(f"{self.text} added to queue ({len(q)} items)")
        try:
            if(event=='mouse press' and button==4):
                listwalker.set_focus(listwalker.next_position(listwalker.get_focus()[1]))
            if(event=='mouse press' and button==5):
                listwalker.set_focus(listwalker.prev_position(listwalker.get_focus()[1]))
        except IndexError:
            pass

listwalker = 0
loopsong = False
def getSongList(a):
    global listwalker
    global content
    listwalker = urwid.SimpleListWalker(content)
    return urwid.ListBox(listwalker)



nowplayingtext = urwid.Text("osu-cplayer",'center')
def getNowPlaying():
    return urwid.AttrMap(nowplayingtext,'header')

def disp_notif(event):
    storeDefText = nowplayingtext.text
    nowplayingtext.set_text(event)
    mainloop.set_alarm_in(1,remove_notif)

def remove_notif(a,b):
    if(songPlaying==0):
        nowplayingtext.set_text("osu-cplayer")
    else:
        nowplayingtext.set_text(songPlaying)

progbar = 0
barAlarm = 0

def pptime(sec):
    m,s = [int(i) for i in divmod(sec,60)]
    if s==0:
        s = "00"
    elif s<10:
        s = str(0)+str(s)
    return f"{m}:{s}"

class SongBar(urwid.ProgressBar):
    global progress
    def get_text(self):
        if songPlaying==0:
                return f"{len(names)} songs available (Press ? for help)"
        if loopsong:
            return f"{pptime((progress/100)*durdict[songPlaying])}/{pptime(durdict[songPlaying])} [looping]"
        return f"{pptime((progress/100)*durdict[songPlaying])}/{pptime(durdict[songPlaying])}"

def updateBar(a,b):
    global barAlarm
    global progress
    if not player.pause:
        progress = (((time.time()-realSongStart)-pauseTime)/durdict[songPlaying])*100
        progbar.set_completion(progress)
    if int(progress)==100:
        nextsong(0,0)
        return 0
    barAlarm = mainloop.set_alarm_in(0.1,updateBar)

def getSongProgress():
    global progbar
    progbar = SongBar('barIncomplete','barComplete')
    return progbar

def getHeader():
    header = urwid.Pile([getNowPlaying(),getSongProgress()])
    return header

def filterSongs(term):
    global names
    names = [i for i in rawnames if term in i]
    listwalker.clear()
    for i in names:
        listwalker.append(urwid.AttrMap(Song(i),"","select"))
    if(len(listwalker)>=1):
        listwalker.set_focus(0)

class FilterEdit(urwid.Edit):
    def keypress(self, size, key):
        if key=='backspace':
            self.edit_text = self.edit_text[:-1]
        elif key=='esc':
            self.edit_text = ""
            frame.focus_position = 'body'
        elif len(key)==1:
            self.edit_text += key
        else:
            frame.focus_position = 'body'
        filterSongs(self.edit_text)

filteredit = 0
def filterInput():
    global filteredit
    filteredit = FilterEdit("filter(:) ")
    return urwid.AttrMap(filteredit,'footer')

def getFooter():
    return filterInput()

def listener(key):
    global loopsong
    global filteredit
    if(key in {'q','ctrl `1c'}):
        raise urwid.ExitMainLoop()
    if(key=='esc'):
        if(names!=rawnames):
            filterSongs("")
            filteredit.edit_text = ""
        else:
            raise urwid.ExitMainLoop()
    if(key=='p'):
        pause()
    if(key=='right'):
        nextsong(0,1)
    if(key=='left'):
        prevsong()
    if(key=='l'):
        loopsong = not loopsong
    if(key=='s'):
        shuffle()
    if(key=='S'):
        sort()
    if(key==":"):
        frame.focus_position = 'footer'
    if(key=="?"):
        webbrowser.open_new_tab("https://github.com/eshanrh/osu-cplayer#controls")
    if(key=="A"):
        disp_notif("Queue cleared")
        q.clear()

a = 0
player = mpv.MPV(input_default_bindings=True, input_vo_keyboard=True)
q = deque()
qhistory = []
rawnames,namedict,durdict = getSongs()
names = rawnames.copy()

content = [urwid.AttrMap(Song(name),"","select") for name in names]
palette = [('select', 'black', 'dark cyan','standout'),
           ('header','black','light gray'),
           ('barIncomplete','black','light gray'),
           ('barComplete','black','light green'),
           ('footer','black','light gray')
]
listBox = getSongList(a)
frame = urwid.Frame(listBox,header=getHeader(),footer=getFooter())
mainloop = urwid.MainLoop(frame,unhandled_input=listener,palette=palette)
mainloop.run()
player.terminate()
