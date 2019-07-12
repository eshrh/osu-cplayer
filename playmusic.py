import os
from pathlib import Path
import mpv
import urwid
import time
import queue
from locale import setlocale, LC_NUMERIC
from tinytag import TinyTag as tag

setlocale(LC_NUMERIC, "C")

global names
global namedict
a = 0

global player
player = mpv.MPV(input_default_bindings=True, input_vo_keyboard=True)

global q
q = queue.Queue()

qhistory = []

def getSongs():
    cur = os.path.abspath("..")
    songdirs = [i for i in [j for j in os.walk(cur)][0][1] if i.split()[0].isdigit() and not i.endswith("[no video]")]
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
    for pos,i in enumerate(songdirs):
        temp = i
        if(i.endswith("[no video]")):
            temp = temp[:-10]
        temp = " ".join(temp.split()[1:])
        names.append(temp)
        namedict[temp] = audios[pos]
    return (sorted(names),namedict)

names,namedict = getSongs()
durdict = {}

def play(name):
    player.play(str(namedict[name]))
    return 0

class Song(urwid.Text):
    def selectable(self):
        return True
    def keypress(self, size, key):
        if(key=='enter'):
            play(self.text)
        if(key=='a'):
            q.put_nowait(self.text)
        return key


def getSongList(content,a):
    return urwid.ListBox(urwid.SimpleListWalker(content))

def listener(key):
    if(key in {'q','esc','ctrl c'}):
        raise urwid.ExitMainLoop()
    if(key=='p'):
        player.pause = not player.pause
    if(key=='right'):
        if not q.empty():
            play(q.get_nowait())


def start():
    content = [urwid.AttrMap(Song(name),"","reveal focus") for name in names]
    palette = [('reveal focus', 'black', 'dark cyan','standout')]
    urwid.MainLoop(getSongList(content,a),unhandled_input=listener,palette=palette).run()
    player.terminate()

start()
