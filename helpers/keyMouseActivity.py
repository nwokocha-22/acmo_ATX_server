
from dataclasses import dataclass, field
from pynput import keyboard, mouse
from threading import Thread
import time
from statistics import mean

@dataclass
class MouseActivity:

    _mouse_move_count: int = field(default=0)
    
    def __init__(self) -> None:
        m = Thread(target=self.mouseMonitor)
        m.start()
        

    @staticmethod
    def on_click(x, y, button, pressed):
        if button == mouse.Button.left:
            MouseActivity._mouse_move_count += 1

        elif button == mouse.Button.right:
            MouseActivity._mouse_move_count += 1

    @staticmethod
    def on_move(x, y):
        MouseActivity._mouse_move_count += 1
        print(x, y)

    def mouseMonitor(self):
        print("mouse monitored")
        """
        Listens for mouse input
        """
        with mouse.Listener(on_click=self.on_click, on_move=self.on_move) as mouseMonitor:
            mouseMonitor.join()

@dataclass
class KeyboardActivity:

    _key_stroke_count: int = field(repr = False, default = 0) 
    
    def __init__(self):
        k = Thread(target = self.keyMonitor)
        k.start()


    @staticmethod
    def on_press(key):
        KeyboardActivity._key_stroke_count += 1
        print(key)
        

    @staticmethod
    def on_release(key):
        if key == keyboard.Key.esc: 
            return False
    
    def keyMonitor(self):
        print("keyboard monitored")
        """
        Listens for keyboard inputs
        """
        with keyboard.Listener(on_press= self.on_press, on_release=self.on_release) as keyMonitor:
            keyMonitor.join()

class KeyMouseMonitor(KeyboardActivity, MouseActivity):

    def __init__(self):
        KeyboardActivity.__init__(self)
        MouseActivity.__init__(self)
        
       
    @property
    def get_mouseCount(self):
        return self._mouse_move_count
    
    @property
    def get_keyStrokeCount(self):
        return self._key_stroke_count

    @get_mouseCount.setter
    def mouseCount(self, value):
        self._mouse_move_count = value

    @get_keyStrokeCount.setter
    def keyStrokeCount(self, value):
        self._key_stroke_count = value

    def getAverage(self, time=60):
        """ 
        Gets the average key stroke and mouse move per minute or hour 
        ----------------
        parameter:
            :time: the interval to estimate average (default = 60 minutes)
        ---------------
        return:
            :avrg_KeyStroke: average key stroke per minute
            :avrg_mouseMove: average mouse move per minute
        """

        key_stroke = self.get_keyStrokeCount
        mouse_move = self.get_mouseCount

        avrg_keyStroke = key_stroke // time
        avrg_mouseMove = mouse_move // time

        self.keyStrokeCount = 0
        self.mouseCount = 0

        return avrg_keyStroke, avrg_mouseMove


# if __name__=="__main__":
#     monitor =KeyMouseMonitor()
#     while True:
#         key_count = monitor.get_keyStrokeCount
#         mouse_count = monitor.get_mouseCount
#         print(f"key count:{key_count}\nmouse count:{mouse_count}")
#         time.sleep(5)
    
    