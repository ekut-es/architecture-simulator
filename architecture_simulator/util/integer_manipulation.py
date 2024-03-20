from __future__ import annotations
from typing import TYPE_CHECKING

from fixedint import UInt8, UInt16, UInt32

if TYPE_CHECKING:
    from architecture_simulator.uarch.memory.decoded_address import DecodedAddress


class ByteOffsetError(ValueError):
    def __init__(self, offset, max) -> None:
        self.offset = offset
        self.max_offset = max

    def __repr__(self) -> str:
        return f"The specified offset of {self.offset} byte{'' if self.offset == 1 else 's'} is illegal since the operation would cross a word boundary. The maximum allowed offset is {self.max_offset} bytes."


def byte_from_block(decoded_address: DecodedAddress, block: list[UInt32]) -> UInt8:
    return UInt8(
        int(block[decoded_address.block_offset]) >> (decoded_address.byte_offset * 8)
    )


def halfword_from_block(decoded_address: DecodedAddress, block: list[UInt32]) -> UInt16:
    if decoded_address.byte_offset > 2:
        raise ByteOffsetError(decoded_address.byte_offset, 2)
    return UInt16(
        int(block[decoded_address.block_offset]) >> (decoded_address.byte_offset * 8)
    )


def word_from_block(decoded_address: DecodedAddress, block: list[UInt32]) -> UInt32:
    if decoded_address.byte_offset != 0:
        raise ByteOffsetError(decoded_address.byte_offset, 0)
    return block[decoded_address.block_offset]


def byte_into_block(
    decoded_address: DecodedAddress, block: list[UInt32], byte: UInt8
) -> list[UInt32]:
    word = int(block[decoded_address.block_offset])
    word = word & (~(0xFF << (decoded_address.byte_offset * 8)))
    word = word | (int(byte) << (decoded_address.byte_offset * 8))
    block[decoded_address.block_offset] = UInt32(word)
    return block


def halfword_into_block(
    decoded_address: DecodedAddress, block: list[UInt32], halfword: UInt16
) -> list[UInt32]:
    if decoded_address.byte_offset > 2:
        raise ByteOffsetError(decoded_address.byte_offset, 2)
    word = int(block[decoded_address.block_offset])
    word = word & (~(0xFFFF << (decoded_address.byte_offset * 8)))
    word = word | (int(halfword) << (decoded_address.byte_offset * 8))
    block[decoded_address.block_offset] = UInt32(word)
    return block


def word_into_block(
    decoded_address: DecodedAddress, block: list[UInt32], word: UInt32
) -> list[UInt32]:
    if decoded_address.byte_offset != 0:
        raise ByteOffsetError(decoded_address.byte_offset, 0)
    block[decoded_address.block_offset] = word
    return block
