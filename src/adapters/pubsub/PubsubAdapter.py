from abc import ABC, abstractmethod

class PubsubAdapter(ABC):
    @abstractmethod
    def publish(self, group, channel, payload):
        pass

    @abstractmethod
    def consume(self, group, channel, handler):
        pass

    @abstractmethod
    def decode(self, msg):
        pass

    @abstractmethod
    async def reply(self, msg, payload):
        pass
