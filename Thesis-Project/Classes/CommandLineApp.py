from abc import ABC, abstractmethod

class CommandLineApp(ABC):

    @abstractmethod
    def process_commands(self, commands: list) -> int:
        pass

    @abstractmethod
    def display_commands(self) -> None:
        pass

