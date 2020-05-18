import os
from pathlib import Path
import random
import webbrowser
import time
import shutil
import struct
import hashlib
import urwid
from tinytag import TinyTag as tag
import mpv
import sys
from collections import deque
from locale import setlocale, LC_NUMERIC

if not os.path.exists(os.path.expanduser("~/.osupaths")):
    with open(os.path.expanduser("~/.osupaths"),"a+") as f:
        print("paths have not been set.")
        ABSPATH_TO_SONGS=input("enter absolute path to songs folder: ")
        ABSPATH_TO_COLLECTIONS=input("enter absolute path to collections.db: ")
        ABSPATH_TO_OSU=input("enter absolute path to osu!.db: ")
        f.write(ABSPATH_TO_SONGS+"\n")
        f.write(ABSPATH_TO_COLLECTIONS+"\n")
        f.write(ABSPATH_TO_OSU+"\n")
else:
    with open(os.path.expanduser("~/.osupaths"),"r+") as f:
        lines = f.readlines()
        ABSPATH_TO_SONGS,ABSPATH_TO_COLLECTIONS,ABSPATH_TO_OSU=[i.strip() for i in lines]

def getSongs():
    cur = ABSPATH_TO_SONGS
    osudb = OsuDbReader(ABSPATH_TO_OSU)
    beatmaps = osudb.read_all_beatmaps()
    marks = []
    seenID = []
    namedict = {}
    durdict = {}
    osudict = {}
    timedict = {}
    names = []
    for n,i in enumerate(beatmaps):
        if i['set_id'] in seenID:
            marks.append(n)
        else:
            seenID.append(i['set_id'])
    for i in sorted(marks,reverse=True):
        beatmaps.pop(i)
    for i in beatmaps:
        try:
            audio = Path(os.path.join(cur,i['folder_name'],i['audio_file']))
            if not audio.is_file():
                audio_with_capital_a = Path(os.path.join(cur,i['folder_name'],i['audio_file'].capitalize()))
                if audio_with_capital_a.is_file():
                    audio = audio_with_capital_a
                else:
                    continue
            name = i['artist']+" - "+i['title']
            if name in names:
                name = name+" ["+str(i['set_id'])+"]"
            names.append(name)
            namedict[name] = audio
            durdict[name] = tag.get(audio).duration
            osudict[name] = Path(os.path.join(cur,i['folder_name'],i['osu_file']))
            timedict[name] = i['last_modification_time']
        except TypeError:
            pass
    return (names,namedict,durdict,osudict,timedict)



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
def sortByDate():
    global names
    names = [x for _,x in sorted(zip([timedict[i] for i in names],names),reverse=True)]
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

def showCollection(c):
    global names
    names = []
    for i in rawnames:
        try:
            for j in md5s[i]:
                if j in collections[c]:
                    names.append(i)
                    break
        except KeyError:
            pass
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
            editboxtext = "filter(:) "
            frame.focus_position = 'body'
        elif len(key)==1:
            self.edit_text += key
        elif key=='down':
            footer.focus_position = 1
        else:
            frame.focus_position = 'body'
        filterSongs(self.edit_text)

class CollectionEdit(urwid.Edit):
    def keypress(self, size, key):
        if key=='backspace':
            self.edit_text = self.edit_text[:-1]
        elif key=='esc':
            self.edit_text = ""
            editboxtext = "filter(:) "
            frame.focus_position = 'body'
        elif len(key)==1:
            self.edit_text += key
        elif key=='enter':
            showCollection(self.edit_text)
        elif key=='up':
            footer.focus_position = 0
        else:
            frame.focus_position = 'body'

filteredit = 0
def filterInput():
    global filteredit
    filteredit = FilterEdit("filter(:) ")
    return urwid.AttrMap(filteredit,'footer')

collectionedit = 0
def collectionInput():
    global collectionedit
    collectionedit = CollectionEdit("Enter collection name(c): ")
    return urwid.AttrMap(collectionedit,'footer')

footer = 0
def getFooter():
    global footer
    footer = urwid.Pile([filterInput(),collectionInput()])
    return footer

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
    if(key=='d'):
        sortByDate()
    if(key==":"):
        frame.focus_position = 'footer'
        footer.focus_position = 0
    if(key=="c"):
        frame.focus_position = 'footer'
        footer.focus_position = 1
    if(key=="?"):
        webbrowser.open_new_tab("https://github.com/eshanrh/osu-cplayer#controls")
    if(key=="A"):
        disp_notif("Queue cleared")
        q.clear()
    if(key=="r"):
        if(songPlaying!=0):
            play(songPlaying)
def md5(fname):
    hash_md5 = hashlib.md5()
    if not os.path.exists(fname):
       return 0
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def generateHashes(osudict):
    md5s = {}
    for i in osudict:
        md5s[i] = md5(osudict[i])
    return md5s

def nextint(f):
    return struct.unpack("<I",f.read(4))[0]
def nextstr(f):
    if f.read(1)==0x00:
        return
    len = 0
    shift = 0
    while(True):
        byte = ord(f.read(1))
        len |= (byte & 0b01111111) <<shift
        if (byte & 0b10000000)==0:
            break
        shift+=7
    return f.read(len).decode('utf-8')

def getCollections():
    col = {}
    f = open(ABSPATH_TO_COLLECTIONS,"rb")
    nextint(f)
    ncol = nextint(f)
    for i in range(ncol):
        colname = nextstr(f)
        col[colname] = []
        for j in range(nextint(f)):
            f.read(2)
            col[colname].append(f.read(32).decode('utf-8'))
    f.close()
    return col

def getDateAdded():
    osudb = OsuDbReader(ABSPATH_TO_OSU)
    times = osudb.read_all_beatmaps()
    timesdict = {}
    return timesdict

class BasicDbReader:
    def __init__(self, file):
        """
        Initializes a BasicDbReader on the given file.
        :param file: path to the db file
        """
        if not file or not os.path.exists(file):
            raise FileNotFoundError('Could not find from the specified file "%s"' % file)
        self.file = open(file, mode='rb')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()

    def read_byte(self):
        """
        Read one Byte from the database-file
        """
        return int.from_bytes(self.file.read(1), byteorder='little')

    def read_short(self):
        """
        Read a Short (2 Byte) from the database-file
        """
        return int.from_bytes(self.file.read(2), byteorder='little')

    def read_int(self):
        """
        Read an Integer (4 Bytes) from the database-file
        """
        return int.from_bytes(self.file.read(4), byteorder='little')

    def read_long(self):
        """
        Read a Long (8 bytes) from the database-file
        """
        return int.from_bytes(self.file.read(8), byteorder='little')

    def read_uleb128(self):
        """
        Read a ULEB128 (variable) from the database-file
        """
        result = 0
        shift = 0
        while True:
            byte = int.from_bytes(self.file.read(1), byteorder='little')
            result |= ((byte & 127) << shift)
            if (byte & 128) == 0:
                break
            shift += 7
        return result

    def read_single(self):
        """
        Read a Single (4 bytes) from the database-file
        """
        return struct.unpack('f', self.file.read(4))[0]

    def read_double(self):
        """
        Read a Double (8 bytes) from the database-file
        """
        return struct.unpack('d', self.file.read(8))[0]

    def read_boolean(self):
        """
        Read a Boolean (1 byte) from the database-file
        """
        return self.read_byte() != 0

    def read_string(self):
        """
        Read a string (variable) from the database-file
        """
        if self.read_byte() == 0x0b:
            length = self.read_uleb128()
            return self.file.read(length).decode('utf8')

    def read_datetime(self):
        """
        Read a Datetime from the database-file
        """
        return self.read_long()
class OsuDbReader(BasicDbReader):
    def __init__(self, file=None):
        super(OsuDbReader, self).__init__(file)
        self.version = self.read_int()
        self.folder_count = self.read_int()
        self.unlocked = self.read_boolean()
        self.date_unlocked = self.read_datetime()
        self.player = self.read_string()
        self.num_beatmaps = self.read_int()
        self.beatmaps = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()

    def read_int_double_pair(self):
        """
        Read an int-double-pair (14 bytes) from the database-file
        :return: a tuple with the int and the double
        """
        if self.read_byte() != 0x08:
            raise Exception('Error while parsing db.')

        first = self.read_int()
        if self.read_byte() != 0x0d:
            raise Exception('Error while parsing db.')
        second = self.read_double()
        return first, second

    def _read_timingpoint(self):
        """
        Read a Timingpoint (17 bytes) from the database-file
        :return: a dict containing bpm, offset and whether the timingpoint is inherited
        """
        bpm = self.read_double()
        offset = self.read_double()
        inherited = self.read_boolean()

        return {
            'bpm': bpm,
            'offset': offset,
            'inherited': inherited
        }

    def read_beatmap(self):
        """
        Read one Beatmap from the database-file
        :return: a (big) dict representing the beatmap
        """
        if len(self.beatmaps) >= self.num_beatmaps:
            return
        if(self.version<=20191106):
            entry_size = self.read_int()
        artist = self.read_string()
        artist_unicode = self.read_string()
        title = self.read_string()
        title_unicode = self.read_string()
        creator = self.read_string()
        difficulty = self.read_string()
        audio_file = self.read_string()
        md5 = self.read_string()
        osu_file = self.read_string()
        ranked_status = self.read_byte()
        circle_count = self.read_short()
        slider_count = self.read_short()
        spinner_count = self.read_short()
        last_modification_time = self.read_long()
        ar = self.read_single()
        cs = self.read_single()
        hp = self.read_single()
        od = self.read_single()
        slider_velocity = self.read_double()

        # Difficulties in respect with the selected mod
        difficulties_std = {}
        difficulties_taiko = {}
        difficulties_ctb = {}
        difficulties_mania = {}

        length = self.read_int()
        for _ in range(length):
            mode, diff = self.read_int_double_pair()
            difficulties_std[mode] = diff

        length = self.read_int()
        for _ in range(length):
            mode, diff = self.read_int_double_pair()
            difficulties_taiko[mode] = diff

        length = self.read_int()
        for _ in range(length):
            mode, diff = self.read_int_double_pair()
            difficulties_ctb[mode] = diff

        length = self.read_int()
        for _ in range(length):
            mode, diff = self.read_int_double_pair()
            difficulties_mania[mode] = diff

        drain_time = self.read_int()
        total_time = self.read_int()
        preview_time = self.read_int()

        # Timingpoints
        timing_points = []
        length = self.read_int()
        for _ in range(length):
            timing_points.append(self._read_timingpoint())

        map_id = self.read_int()
        set_id = self.read_int()
        thread_id = self.read_int()
        grade_std = self.read_byte()
        grade_taiko = self.read_byte()
        grade_ctb = self.read_byte()
        grade_mania = self.read_byte()
        local_offset = self.read_short()
        stack_leniency = self.read_single()
        game_mode = self.read_byte()  # 0x00 = osu!Standard, 0x01 = Taiko, 0x02 = CTB, 0x03 = Mania
        song_source = self.read_string()
        song_tags = self.read_string()
        online_offset = self.read_short()
        font = self.read_string()  # Why do you even need this -_-
        unplayed = self.read_boolean()
        last_played = self.read_long()
        osz2 = self.read_boolean()
        folder_name = self.read_string()
        last_checked = self.read_long()
        ignore_map_sound = self.read_boolean()
        ignore_map_skin = self.read_boolean()
        disable_storyboard = self.read_boolean()
        disable_video = self.read_boolean()
        visual_override = self.read_boolean()  # I have no idea what that is supposed to be
        last_modification_time_2 = self.read_int()  # I swear we had this already
        mania_scroll_speed = self.read_byte()

        beatmap = {'artist': artist, 'artist_unicode': artist_unicode, 'title': title,
                   'title_unicode': title_unicode, 'creator': creator, 'difficulty': difficulty,
                   'audio_file': audio_file, 'md5': md5, 'osu_file': osu_file, 'ranked_status': ranked_status,
                   'circle_count': circle_count, 'slider_count': slider_count, 'spinner_count': spinner_count,
                   'last_modification_time': last_modification_time, 'ar': ar, 'cs': cs, 'hp': hp, 'od': od,
                   'slider_velocity': slider_velocity, 'difficulties_std': difficulties_std,
                   'difficulties_taiko': difficulties_taiko, 'difficulties_ctb': difficulties_ctb,
                   'difficulties_mania': difficulties_mania, 'drain_time': drain_time, 'total_time': total_time,
                   'preview_time': preview_time, 'timing_points': timing_points, 'map_id': map_id, 'set_id': set_id,
                   'thread_id': thread_id, 'grade_std': grade_std, 'grade_taiko': grade_taiko, 'grade_ctb': grade_ctb,
                   'grade_mania': grade_mania, 'local_offset': local_offset, 'stack_leniency': stack_leniency,
                   'game_mode': game_mode, 'song_source': song_source, 'song_tags': song_tags,
                   'online_offset': online_offset, 'font': font, 'unplayed': unplayed, 'last_played': last_played,
                   'osz2': osz2, 'folder_name': folder_name, 'last_checkee': last_checked,
                   'ignore_map_sound': ignore_map_sound, 'ignore_map_skin': ignore_map_skin,
                   'disable_storyboard': disable_storyboard, 'disable_video': disable_video,
                   'visual_override': visual_override, 'last_modification_time_2': last_modification_time_2,
                   'mania_scroll_speed': mania_scroll_speed}
        self.beatmaps.append(beatmap)
        return beatmap

    def read_all_beatmaps(self):
        for i in range(self.num_beatmaps - len(self.beatmaps)):
            self.read_beatmap()
        return self.beatmaps



def main():
    global a,player,q,qhistory,rawnames,namedict,durdict,osudict,timedict,content,md5s
    global collections,names,content,palette,listBox,frame,mainloop
    a = 0
    player = mpv.MPV(input_default_bindings=True, input_vo_keyboard=True)
    q = deque()
    qhistory = []
    getSongs()
    rawnames,namedict,durdict,osudict,timedict = getSongs()

    md5s = generateHashes(osudict)

    collections = getCollections()
    getDateAdded()

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
