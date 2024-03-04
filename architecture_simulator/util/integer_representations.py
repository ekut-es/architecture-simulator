import math


def get_12_bit_representations(number: int) -> tuple[str, str, str, str]:
    """Shorthand function for get_n_bit_representations(number, n=12)"""
    return get_n_bit_representations(number=number, n=12)


def get_16_bit_representations(number: int) -> tuple[str, str, str, str]:
    """Shorthand function for get_n_bit_representations(number, n=16)"""
    return get_n_bit_representations(number=number, n=16)


def get_32_bit_representations(number: int) -> tuple[str, str, str, str]:
    """Shorthand function for get_n_bit_representations(number, n=32)"""
    return get_n_bit_representations(number=number, n=32)


def get_n_bit_representations(number: int, n: int) -> tuple[str, str, str, str]:
    """Returns (bin, udec, hex, sdec) representations for the given number, assuming the number has n bits. Twos complement is used for bin and hex strings.

    Args:
        number (int): The number to get the representations for. May be negative or require more bits than n.
        n (int): The number of bits to use for the representation.

    Returns:
        tuple[str, str, str, str]: (bin, udec, hex, sdec) representations for number.
        hex and bin strings will be sign extended to given n and will have spaces inserted after every 8 (for bin) or 2 (for hex) characters.
    """
    unsigned_number = number & (2**n - 1)
    signed_number = (
        unsigned_number - 2**n if unsigned_number >= 2 ** (n - 1) else unsigned_number
    )
    bin_format = "{:0" + str(n) + "b}"
    bin_string = bin_format.format(unsigned_number)
    hex_string = to_hex_str(unsigned_number, n)
    return (
        groupify_string(string=bin_string, group_size=8),
        str(unsigned_number),
        groupify_string(string=hex_string, group_size=2),
        str(signed_number),
    )


def to_hex_str(number: int, n: int) -> str:
    """Returns the number as hex string, padded to contain the given number of BITS (not hex chars).

    Args:
        number (int): number to convert.
        n (int): number of bits the number should be padded to (4 per character).

    Returns:
        str: The padded string.
    """
    hex_format = "{:0" + str(math.ceil(n / 4)) + "X}"
    return hex_format.format(number)


def groupify_string(string: str, group_size: int, separator=" ") -> str:
    """Inserts the separator after every group_size characters, going from right to left.

    Example:
        groupify_string("1110000", 4) = "111 0000"

    Args:
        string (str): String to groupify
        group_size (int): Size of the groups. Must be greater or equal to 1.
        separator (str): The string to insert between groups.

    Returns:
        str: The grouped string.
    """
    reversed_string = string[::-1]
    num_groups = math.ceil((len(reversed_string) / group_size))
    grouped_string = separator.join(
        reversed_string[i * group_size : (i + 1) * group_size]
        for i in range(num_groups)
    )
    return grouped_string[::-1]
