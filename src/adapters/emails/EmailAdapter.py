from abc import ABC, abstractmethod

class EmailAdapter(ABC):
    @abstractmethod
    def is_disabled(self):
        pass

    @abstractmethod
    def send(self, email):
        pass
