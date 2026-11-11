from __future__ import annotations

import struct

from ._shared import (BitReader, BitWriter, build_canonical, decoder_for,
                      parse_lengths, serialize_lengths)


def v4_huffman_canonical_compress(data: bytes) -> bytes:
    codes = build_canonical(data)
    writer = BitWriter()
    for symbol in data:
        bits, width = codes[symbol]
        writer.write(bits, width)
    return (b'HC04' + struct.pack('>I', len(data)) +
            serialize_lengths(codes, 1) + writer.finish())


def v4_huffman_canonical_decompress(packet: bytes) -> bytes:
    if len(packet) < 8 or packet[:4] != b'HC04':
        raise ValueError('Invalid canonical Huffman packet')
    n = struct.unpack_from('>I', packet, 4)[0]
    codes, cursor = parse_lengths(packet, 8, 1)
    read_symbol = decoder_for(codes)
    reader = BitReader(packet[cursor:])
    return bytes(read_symbol(reader) for _ in range(n))
