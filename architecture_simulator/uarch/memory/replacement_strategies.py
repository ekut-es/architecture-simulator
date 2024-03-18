from typing import Any
from abc import ABC, abstractmethod
import math


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

    @abstractmethod
    def get_repr(self) -> Any:
        """Return some form of representation for the state of the strategy.

        Returns:
            Any:
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

    def get_repr(self) -> list[int]:
        """Returns the lru value for each block. The least recently used block has the value 0,
        older blocks have higher values.

        Returns:
            list[int]: A list of lru values.
        """
        return [self.lru.index(i) for i in range(len(self.lru))]


class PLRU(ReplacementStrategy):
    def __init__(self, associativity: int) -> None:
        # ensure associativity is a power of two and not zero
        assert (associativity != 0) and ((associativity & (associativity - 1)) == 0)

        super().__init__(associativity)
        self.tree_array = [False] * (associativity - 1)
        self.tree_depth = int(math.log2(self.associativity))

    def access(self, index: int) -> None:
        assert index >= 0

        i = index + self.associativity - 1
        for _ in range(self.tree_depth):
            is_right_child = i % 2 == 0
            i = (i - 1) // 2
            self.tree_array[i] = is_right_child

    def get_next_to_replace(self) -> int:
        i = 0
        for _ in range(self.tree_depth):
            if self.tree_array[i]:
                i = 2 * i + 1
            else:
                i = 2 * i + 2
        return i + 1 - self.associativity

    def get_repr(self) -> Any:
        return None
