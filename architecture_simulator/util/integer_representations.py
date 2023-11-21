def get_12_bit_representations(number: int) -> tuple[str, str, str, str]:
    """Converts an int into a representation tuple, assuming it has 12 bits.

    Args:
        number (int): number to make representations from.

    Returns:
        tuple[str, str, str, str]: (bin, udec, hex, sdec)
    """
    unsigned_number = number & (2**12 - 1)
    signed_number = (
        unsigned_number - 2**12 if unsigned_number >= 2**11 else unsigned_number
    )
    bin_number = "{:012b}".format(unsigned_number)
    hex_number = "{:03X}".format(unsigned_number)
    return (
        f"{bin_number[:4]} {bin_number[4:]}",
        str(unsigned_number),
        f"{hex_number[0]} {hex_number[1:]}",
        str(signed_number),
    )


def get_16_bit_representations(number: int) -> tuple[str, str, str, str]:
    """Converts an int into a representation tuple, assuming it has 16 bits.

    Args:
        number (int): number to make representations from.

    Returns:
        tuple[str, str, str, str]: (bin, udec, hex, sdec)
    """
    unsigned_number = number & (2**16 - 1)
    signed_number = (
        unsigned_number - 2**16 if unsigned_number >= 2**15 else unsigned_number
    )
    bin_number = "{:016b}".format(unsigned_number)
    hex_number = "{:04X}".format(unsigned_number)
    return (
        f"{bin_number[:8]} {bin_number[8:]}",
        str(unsigned_number),
        f"{hex_number[:2]} {hex_number[2:]}",
        str(signed_number),
    )
