from abc import ABC, abstractmethod

class AIPlatform(ABC):

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass