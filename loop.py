class Looper:
    def __init__(self, cb):
        self.cb = cb
        assert 'handle' in dir(self.cb)

    def go(self):
        while 1:
            s = input()
            self.cb.handle(s)
            if s == 'q':
                return
