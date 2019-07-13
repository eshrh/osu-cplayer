import urwid
import random
import time

class RandomText(urwid.Text):
    def refresh(self):
        self.text = random.randint(0,10)
def getContent():
    return urwid.Filler(RandomText(""), 'top')

loop = urwid.MainLoop(getContent())
loop.run()
while True:
    loop.draw_screen()
    time.sleep(0.2)
