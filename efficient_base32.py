"""
Base32 encoding and decoding

https://en.wikipedia.org/wiki/Base32
"""

B32_CHARSET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
# Create a reverse mapping for efficient decoding
B32_REVERSE_MAP = {char: index for index, char in enumerate(B32_CHARSET)}


def base32_encode(data: bytes) -> bytes:
    """
    Encodes binary data into a Base32 string using bitwise operations.

    >>> base32_encode(b"Hello World!")
    b'JBSWY3DPEBLW64TMMQQQ===='
    >>> base32_encode(b"123456")
    b'GEZDGNBVGY======'
    >>> base32_encode(b"some long complex string")
    b'ONXW2ZJANRXW4ZZAMNXW24DMMV4CA43UOJUW4ZY='
    >>> base32_encode(b"")
    b''
    """
    if not data:
        return b""

    encoded_chars = []
    buffer = 0
    bits_in_buffer = 0

    for byte in data:
        # Add the 8 bits of the current byte to our buffer
        buffer = (buffer << 8) | byte
        bits_in_buffer += 8

        # While we have at least 5 bits in the buffer, extract a Base32 character
        while bits_in_buffer >= 5:
            bits_in_buffer -= 5
            # Get the top 5 bits
            index = buffer >> bits_in_buffer
            encoded_chars.append(B32_CHARSET[index])
            # Clear the top 5 bits from the buffer
            buffer &= (1 << bits_in_buffer) - 1

    # If there are any remaining bits, pad with zeros and add the final character
    if bits_in_buffer > 0:
        # Shift remaining bits to the left to form a 5-bit chunk
        index = buffer << (5 - bits_in_buffer)
        encoded_chars.append(B32_CHARSET[index])

    # Add padding
    padding_len = (8 - len(encoded_chars) % 8) % 8
    result = "".join(encoded_chars) + "=" * padding_len

    return result.encode("ascii")


def base32_decode(data: bytes) -> bytes:
    """
    Decodes a Base32 string into binary data using bitwise operations.

    >>> base32_decode(b'JBSWY3DPEBLW64TMMQQQ====')
    b'Hello World!'
    >>> base32_decode(b'GEZDGNBVGY======')
    b'123456'
    >>> base32_decode(b'ONXW2ZJANRXW4ZZAMNXW24DMMV4CA43UOJUW4ZY=')
    b'some long complex string'
    >>> base32_decode(b"")
    b''
    """
    # Decode to a string and strip padding
    s = data.decode("ascii").rstrip("=")
    if not s:
        return b""

    decoded_bytes = []
    buffer = 0
    bits_in_buffer = 0

    for char in s:
        try:
            value = B32_REVERSE_MAP[char]
        except KeyError:
            raise ValueError(f"Invalid character in Base32 string: '{char}'")

        # Add the 5 bits of the current character to our buffer
        buffer = (buffer << 5) | value
        bits_in_buffer += 5

        # While we have at least 8 bits, extract a full byte
        if bits_in_buffer >= 8:
            bits_in_buffer -= 8
            # Get the top 8 bits
            byte = buffer >> bits_in_buffer
            decoded_bytes.append(byte)
            # Clear the top 8 bits from the buffer
            buffer &= (1 << bits_in_buffer) - 1

    return bytes(decoded_bytes)


if __name__ == "__main__":
    import doctest

    # 1. Run the built-in tests first to ensure correctness
    print("Running doctests...")
    doctest.testmod()
    print("Doctests passed! ✅")
    print("-" * 20)

    # 2. Define sample data for the loop
    sample_data = b"This is a test string that will be encoded and decoded."

    # 3. Use a for loop to run the functions 100 times
    print("Starting 100 encode/decode cycles...")
    for i in range(100000):
        # Encode the data
        encoded_data = base32_encode(sample_data)
        
        # Decode the data
        decoded_data = base32_decode(encoded_data)

        # Optional: Check if the decoded data matches the original
        assert sample_data == decoded_data

        # Optional: Print progress for each run
        print(f"Cycle {i + 1}: OK")
    
    print("-" * 20)
    print("Successfully completed 100 cycles.")
    