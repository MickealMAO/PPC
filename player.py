from collections.abc import Callable, Iterable, Mapping
from multiprocessing import Process
from typing import Any

class Player(Process):
    def __init__(self):
        super().__init__()
    
    def run(self):
        pass

