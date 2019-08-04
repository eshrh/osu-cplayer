# osu-cplayer
Fast and compact command line osu! song player built on mpv

## Dependencies
+ Python 3.6+
+ [mpv](https://mpv.io/installation/)
+ [python-mpv](https://github.com/jaseg/python-mpv) (auto-install)
+ [urwid](https://github.com/urwid/urwid/wiki/Installation-instructions) (auto-install)
+ [tinytag](https://github.com/devsnd/tinytag) (auto-install)

## Usage
1. Download `playmusic.py`
2. Edit `ABSPATH_TO_SONGS` to the absolute path of your osu! songs folder. The default path implies that the script is inside a folder in the Songs directory.
3. Run with `python3 playmusic.py`

## Controls
+ Previous/Next Song: `left`/`right`
+ Move Selection: `up`/`down`, left click, or scroll
+ Play song: `enter` or double click
+ Toggle play/pause: `p`
+ Quit: `q` or `esc`
+ Add song to queue: `a`
+ Clear queue: `A`
+ Shuffle: `s`
+ Sort: `S`
+ Filter: `:` or mouse followed by filter term
	+ Reset filter: `esc`
	+ Exit text box: any special key or mouse
+ Filter by Collection: `c` or mouse, followed by collection name, and `enter`
