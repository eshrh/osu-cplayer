# osu-cplayer
Fast, compact, and featured command line osu! song player built on mpv.
![screenshot](https://github.com/eshrh/osu-cplayer/raw/master/2020-04-23-161205_1920x1080_scrot.png)

## Installation
1. Install osu-cplayer via pip: `pip install osu-cplayer`
2. Install [mpv](https://mpv.io/installation/)
3. On first run, enter the absolute paths of your songs folder, collections.db file and osu!.db file
4. These settings get saved in your home folder as `~/.osupaths` or equivalent.

## Usage
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
+ Open this help page: `?`

## Other
osu!.db reading code is taken from [OsuDbReader](https://github.com/Awlexus/PyOsuDBReader/)

## Dependencies
+ Python 3.6+
+ [python-mpv](https://github.com/jaseg/python-mpv)
+ [urwid](https://github.com/urwid/urwid/wiki/Installation-instructions)
+ [tinytag](https://github.com/devsnd/tinytag)

