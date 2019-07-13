# osu-cplayer
command line osu! song player built on mpv

## Dependencies
+ Python 3.4+
+ [mpv](https://mpv.io/installation/)
+ [python-mpv](https://github.com/jaseg/python-mpv)
+ [urwid](https://github.com/urwid/urwid/wiki/Installation-instructions)
+ [tinytag](https://github.com/devsnd/tinytag)

## Usage
1. Download `playmusic.py`
2. Edit `ABSPATH_TO_SONGS` to the absolute path of your osu! songs folder
3. Run with `python3 playmusic.py`

## Controls
+ Previous/Next Song: `left`/`right`
+ Move Selection: `up`/`down` or left click
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

