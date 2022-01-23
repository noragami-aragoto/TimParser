from abc import ABCMeta, abstractmethod


class ParseDataWriter:
    __metaclass__ = ABCMeta

    @abstractmethod
    def set_path(self): pass

    @abstractmethod
    def save(self, data): pass
