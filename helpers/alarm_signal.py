import time, threading

class _Timer(threading.Thread):
    """
    This thread blocks for the interval specified and set the threading.Event when
    the time elapses

    """
  
    def __init__(self, interval, mode="sec"):
        super(_Timer, self).__init__()

        self._mode = mode
        self.interval = interval
        self.event = threading.Event()
        self.should_run = threading.Event()
        self._init()

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def set_mode(self, value):
        """
        sets a new value to mode; either, seconds, minutes, or hours
        """
        self._mode = value

    def _init(self):
        self.event.clear()
        self.should_run.set()

    def stop(self):
        """
        Stop the this thread. Ensureto call immediatel afterwards
        """
        self.should_run.clear()

    def consume(self):
        was_set = self.event.is_set()
        if was_set:
            self.event.clear()
        return was_set

    def run(self):
        """
        The internal main method of this thread. Block for :attr:`interval`
        seconds before setting :attr:`Ticker.evt`

        :warning::
        Do not call this directly!  Instead call :meth:`start`.
        """
        print("running...")
        interval = self.interval
        if self.mode == "min":
            interval = self.interval * 60
        elif self.mode == "hour":
            interval = self.interval * 60 * 60

        print(self.mode, interval)

        while self.should_run.is_set():
            time.sleep(interval)
            self.event.set()


def timer(func):

    def _timer(callback, interval, mode):

        """
        A decorator function that calls the function after the interval elapses
        -------------
        parameter:
            :callback: the function to be called
            :interval: the specified interval
            :mode: the time frame -> sec, min or hour
        """
       
        _time = _Timer(interval)
        _time.set_mode = mode
        _time.start() 
       
        try:
        
            while _time.event.wait(): # waits until the sets method of the thread event is called
                _time.event.clear() 
                callback()
        except:

            _time.stop() 
            _time.join() 

        return func(callback, interval, mode)
    return _timer

# USE CASE
"""
    def callback():
        print("alarm !!!")

    @timer
    def func(callback, interval, mode):
        print("alarm triggered")

    func(callback, 1, 'sec')
"""
    