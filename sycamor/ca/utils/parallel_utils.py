import threading

class AtomicCounter:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()

    def increment(self, value):
        
        with self._lock:
            self._value += value
            return self._value

    def decrement(self, value):
        
        with self._lock:
            self._value -= value
            return self._value

    @property
    def value(self):
        return self._value