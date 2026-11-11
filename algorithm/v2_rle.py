from __future__ import annotations

import struct

from ._shared import BitReader, BitWriter


def v2_rle_compress(data: bytes) -> bytes:
    """7-bit run count (1..127) + 8-bit byte literal, packed into 15-bit runs.

    Handworked Part A uses 3-bit symbols because its alphabet has only 6 letters.
    """
    writer = BitWriter()
    i = 0
    while i < len(data):
        count = 1
        while i + count < len(data) and count < 127 and data[i + count] == data[i]:
            count += 1
        writer.write(count, 7)
        writer.write(data[i], 8)
        i += count
    return b'RL02' + struct.pack('>I', len(data)) + writer.finish()


def v2_rle_decompress(packet: bytes) -> bytes:
    if len(packet) < 8 or packet[:4] != b'RL02':
        raise ValueError('Invalid RLE packet')
    n = struct.unpack_from('>I', packet, 4)[0]
    reader = BitReader(packet[8:])
    decoded = bytearray()
    while len(decoded) < n:
        count, symbol = reader.read(7), reader.read(8)
        if count == 0 or len(decoded) + count > n:
            raise ValueError('Invalid RLE run')
        decoded.extend(bytes([symbol]) * count)
    return bytes(decoded)
