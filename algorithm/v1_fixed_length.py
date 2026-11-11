from __future__ import annotations

import struct

from ._shared import BitReader, BitWriter


def v1_fixed_length_compress(data: bytes) -> bytes:
    alphabet = bytes(sorted(set(data)))
    m = len(alphabet)
    width = (m - 1).bit_length() if m else 0
    writer = BitWriter()
    index = {symbol: i for i, symbol in enumerate(alphabet)}
    for symbol in data:
        writer.write(index[symbol], width)
    return b'FL01' + struct.pack('>IHB', len(data), m, width) + alphabet + writer.finish()


def v1_fixed_length_decompress(packet: bytes) -> bytes:
    if len(packet) < 11 or packet[:4] != b'FL01':
        raise ValueError('Invalid fixed-length packet')
    n, m, width = struct.unpack_from('>IHB', packet, 4)
    if m > 256 or width != ((m - 1).bit_length() if m else 0) or (n > 0 and m == 0):
        raise ValueError('Invalid alphabet metadata')
    if len(packet) < 11 + m:
        raise ValueError('Truncated alphabet')
    alphabet = packet[11:11 + m]
    reader = BitReader(packet[11 + m:])
    result = bytearray()
    for _ in range(n):
        index = reader.read(width)
        if index >= m:
            raise ValueError('Invalid symbol index')
        result.append(alphabet[index])
    return bytes(result)
