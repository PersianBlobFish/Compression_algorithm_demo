from __future__ import annotations

from collections import Counter
import struct

from ._shared import BitReader, BitWriter, HuffNode, huffman_tree, tree_codes


def write_tree(node: HuffNode, writer: BitWriter) -> None:
    if node.symbol is not None:
        writer.write(1, 1)
        writer.write(node.symbol, 8)
    else:
        writer.write(0, 1)
        write_tree(node.left, writer)
        write_tree(node.right, writer)


def read_tree(reader: BitReader) -> HuffNode:
    if reader.read(1):
        return HuffNode(0, reader.read(8))
    left = read_tree(reader)
    right = read_tree(reader)
    return HuffNode(0, None, left, right)


def v3_huffman_tree_compress(data: bytes) -> bytes:
    writer = BitWriter()
    if data:
        root = huffman_tree(Counter(data))
        write_tree(root, writer)
        codes = tree_codes(root)
        for symbol in data:
            code, width = codes[symbol]
            writer.write(code, width)
    return b'HF03' + struct.pack('>I', len(data)) + writer.finish()


def v3_huffman_tree_decompress(packet: bytes) -> bytes:
    if len(packet) < 8 or packet[:4] != b'HF03':
        raise ValueError('Invalid Huffman tree packet')
    n = struct.unpack_from('>I', packet, 4)[0]
    if n == 0:
        return b''
    reader = BitReader(packet[8:])
    root = read_tree(reader)
    result = bytearray()
    for _ in range(n):
        node = root
        if node.symbol is not None:
            if reader.read(1) != 0:
                raise ValueError('Invalid single-symbol code')
        else:
            while node.symbol is None:
                node = node.right if reader.read(1) else node.left
        result.append(node.symbol)
    return bytes(result)
