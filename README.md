# osu-cplayer
Fast, compact, and featured command line osu! song player built on mpv.
![screenshot](https://github.com/eshrh/osu-cplayer/raw/master/2020-04-23-161205_1920x1080_scrot.png)

## Dependencies
+ Python 3.6+
+ [mpv](https://mpv.io/installation/)
+ [python-mpv](https://github.com/jaseg/python-mpv) (auto-install)
+ [urwid](https://github.com/urwid/urwid/wiki/Installation-instructions) (auto-install)
+ [tinytag](https://github.com/devsnd/tinytag) (auto-install)

## Usage
1. Download `playmusic.py`
2. Edit the following variables:
	1. `ABSPATH_TO_SONGS` to the absolute path of your osu Songs folder
	2. `ABSPATH_TO_COLLECTIONS` to the absolute path of your osu collections.db file
	3. `ABSPATH_TO_OSU` to the absolute path of your osu osu!.db file
3. Run with `python3 playmusic.py` and maybe set an alias for it as well.

## Controls
+ Previous/Next Song: `left`/`right`
+ Move Selection: `up`/`down`, left click, or scroll
+ Play song: `enter` or double click
+ Toggle play/pause: `p`
+ Quit: `q` or `esc`
+ Add song to queue: `a`
+ Clear queue: `A`
+ Shuffle: `s`
+ Sort alphabetically(default): `S`
+ Sort by date added: `d`
+ Filter: `:` or mouse followed by filter term
	+ Reset filter: `esc`
	+ Exit text box: any special key or mouse
+ Filter by Collection: `c` or mouse, followed by collection name, and `enter`

## Other
osu!.db reading code is taken from [OsuDbReader](https://github.com/Awlexus/PyOsuDBReader/)

## TODO
+ Package and upload to pypi
+ Allow setting of global variables via cli switch
