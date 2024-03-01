from __future__ import annotations
from typing import TYPE_CHECKING

from fixedint import UInt8, UInt16, UInt32

if TYPE_CHECKING:
    from architecture_simulator.uarch.cache import DecodedAddress


def byte_from_block(decoded_address: DecodedAddress, block: list[UInt32]) -> UInt8:
    return UInt8(
        int(block[decoded_address.block_offset]) >> (decoded_address.byte_offset * 8)
    )


def halfword_from_block(decoded_address: DecodedAddress, block: list[UInt32]) -> UInt16:
    assert decoded_address.byte_offset <= 2  # TODO: Custom Error
    return UInt16(
        int(block[decoded_address.block_offset]) >> (decoded_address.byte_offset * 8)
    )


def word_from_block(decoded_address: DecodedAddress, block: list[UInt32]) -> UInt32:
    assert decoded_address.byte_offset == 0  # TODO: Custom Error
    return block[decoded_address.block_offset]


def byte_into_block(
    decoded_address: DecodedAddress, block: list[UInt32], byte: UInt8
) -> list[UInt32]:
    word = int(block[decoded_address.block_offset])
    word = word & (~(0xFF << (decoded_address.byte_offset * 8)))
    word = word | (byte << (decoded_address.byte_offset * 8))
    block[decoded_address.block_offset] = UInt32(word)
    return block


def halfword_into_block(
    decoded_address: DecodedAddress, block: list[UInt32], halfword: UInt16
) -> list[UInt32]:
    assert decoded_address.byte_offset <= 2  # TODO: Custom Error
    word = int(block[decoded_address.block_offset])
    word = word & (~(0xFFFF << (decoded_address.byte_offset * 8)))
    word = word | (halfword << (decoded_address.byte_offset * 8))
    block[decoded_address.block_offset] = UInt32(word)
    return block


def word_into_block(
    decoded_address: DecodedAddress, block: list[UInt32], word: UInt32
) -> list[UInt32]:
    assert decoded_address.byte_offset == 0  # TODO: Custom Error
    block[decoded_address.block_offset] = word
    return block
