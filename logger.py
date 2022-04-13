from multiprocessing import Queue

class Logger():
    def __init__(self, externalinterface=True):
        self.mainq = Queue()
        self.externalinterface = externalinterface


    def Log(self, text, type = 'log'):
        el = {'text': text, 'type': type}
        if self.externalinterface:
            self.mainq.put(el)
        else:
            print(el)

    def GetElementToShow(self, blocking = False):
        el= None
        try:
            if blocking:
                el = self.mainq.get()
            else:
                el = self.mainq.get(False,3)
        except:
            pass
        return el