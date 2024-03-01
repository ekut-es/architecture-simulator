from abc import ABC, abstractmethod


class ReplacementStrategy(ABC):
    """A class that stores and updates the state of the replacement strategy for a set of the cache.
    NOTE: All replacement strategies must be idempotent - after the first call to access(), further calls should not change the state
    of the strategy. This is because we may call the read methods of the cache in order to generate values for the visualization in the webui.
    """

    def __init__(self, associativity: int) -> None:
        self.associativity = associativity

    @abstractmethod
    def access(self, index: int) -> None:
        """Informs the replacement strategy that an element has been accessed.
        Needs to be idempotent.

        Args:
            index (int): The index of the block inside the set that was accessed.
        """

    @abstractmethod
    def get_next_to_replace(self) -> int:
        """Returns the index of the block that shall be replaced next.

        Returns:
            int: The index of the block inside the set to be replaced next.
        """


class LRU(ReplacementStrategy):
    def __init__(self, associativity: int) -> None:
        super().__init__(associativity)
        self.lru = [i for i in range(associativity)]

    def access(self, index: int) -> None:
        self.lru.remove(index)
        self.lru.append(index)

    def get_next_to_replace(self) -> int:
        return self.lru[0]
