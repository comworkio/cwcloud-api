from abc import ABC, abstractmethod

from schemas.Ai import PromptSchema

class ModelAdapter(ABC):
    @abstractmethod
    def load_model(self):
        pass

    @abstractmethod
    def generate_response(self, prompt: PromptSchema):
        pass
