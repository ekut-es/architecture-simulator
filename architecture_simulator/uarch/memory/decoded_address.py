from fixedint import UInt32


class DecodedAddress:
    """A class that contains a lot of information about an address that is relevant for caches,
    like the tag, the index and offsets.
    All this information depends on the width of the index and the number of bits used for the block offset.
    """

    def __init__(self, num_index_bits: int, num_block_bits: int, address: int) -> None:
        """Constructs a DecodedAddress object.

        Args:
            num_index_bits (int): The width of the index in bits.
            num_block_bits (int): The number of bits that are used for the block offset.
            address (int): The full address.
        """

        self.full_address: int = int(UInt32(address))
        """The full address"""

        self.num_index_bits = num_index_bits
        """The number of bits for the index."""

        self.num_block_bits = num_block_bits
        """The number of bits for the block index."""

        self.num_tag_bits = 32 - (num_index_bits + num_block_bits + 2)
        """The number of bits for the tag"""

        self.tag: int = self.full_address >> (num_index_bits + num_block_bits + 2)
        """The tag"""

        self.cache_set_index: int = (self.full_address >> (num_block_bits + 2)) & (
            2**num_index_bits - 1
        )
        """The index"""

        self.word_alinged_address: int = self.full_address & 0xFFFFFFFC
        """The address, but with the lower two bits cleared."""

        self.byte_offset: int = self.full_address & 0x3
        """The index of the byte within the word."""

        self.block_alinged_address: int = (
            self.full_address >> (2 + num_block_bits)
        ) << (2 + num_block_bits)
        """The address, but with the bits for the block and byte offsets cleared."""

        self.block_offset: int = (self.full_address >> 2) & (2**num_block_bits - 1)
        """The index of the block within its set."""
