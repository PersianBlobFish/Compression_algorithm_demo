"""Problem 8: five educational, lossless byte codecs.

Authors: student group (fill in names). No third-party dependency.
All codecs return standalone byte packets with enough metadata to decode.
Bit counts in Part A exclude packet headers unless stated otherwise.
"""
from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
import heapq
import math
import struct
from typing import Optional


class BitWriter:
    def __init__(self):
        self.data = bytearray()
        self.accumulator = 0
        self.filled = 0
        self.bits_written = 0

    def write(self, value: int, width: int) -> None:
        if width < 0 or value < 0 or value >= (1 << width):
            raise ValueError(f"Value {value} does not fit in {width} bits")
        self.bits_written += width
        for bit_index in range(width - 1, -1, -1):
            self.accumulator = (self.accumulator << 1) | ((value >> bit_index) & 1)
            self.filled += 1
            if self.filled == 8:
                self.data.append(self.accumulator)
                self.accumulator = 0
                self.filled = 0

    def finish(self) -> bytes:
        if self.filled:
            self.data.append(self.accumulator << (8 - self.filled))
            self.accumulator = 0
            self.filled = 0
        return bytes(self.data)


class BitReader:
    def __init__(self, payload: bytes):
        self.data = payload
        self.pos = 0

    def read(self, width: int) -> int:
        if width < 0 or self.pos + width > 8 * len(self.data):
            raise ValueError("Truncated bitstream")
        value = 0
        for _ in range(width):
            byte = self.data[self.pos >> 3]
            value = (value << 1) | ((byte >> (7 - (self.pos & 7))) & 1)
            self.pos += 1
        return value


@dataclass(slots=True)
class HuffNode:
    weight: int
    symbol: Optional[int] = None
    left: Optional['HuffNode'] = None
    right: Optional['HuffNode'] = None


def huffman_tree(frequencies: dict[int, int]) -> Optional[HuffNode]:
    """Deterministic O(m log m) binary min-heap Huffman construction."""
    heap = []
    serial = 0
    for symbol, count in sorted(frequencies.items()):
        if count <= 0:
            raise ValueError("Frequencies must be positive")
        leaf = HuffNode(count, symbol)
        heapq.heappush(heap, (count, symbol, serial, leaf))
        serial += 1
    while len(heap) > 1:
        wa, mina, _, left = heapq.heappop(heap)
        wb, minb, _, right = heapq.heappop(heap)
        parent = HuffNode(wa + wb, None, left, right)
        heapq.heappush(heap, (wa + wb, min(mina, minb), serial, parent))
        serial += 1
    return heap[0][-1] if heap else None


def tree_codes(node: HuffNode) -> dict[int, tuple[int, int]]:
    codes = {}

    def visit(n: HuffNode, code: int, depth: int) -> None:
        if n.symbol is not None:
            codes[n.symbol] = (code, depth or 1)
        else:
            visit(n.left, code << 1, depth + 1)
            visit(n.right, (code << 1) | 1, depth + 1)

    visit(node, 0, 0)
    return codes


def canonical_codes(lengths: dict[int, int]) -> dict[int, tuple[int, int]]:
    """Sort (length, symbol); first code 0, others (code+1) << length jump."""
    if not lengths:
        return {}
    sorted_items = sorted(lengths.items(), key=lambda e: (e[1], e[0]))
    output = {}
    prior_length = sorted_items[0][1]
    if not 1 <= prior_length <= 255:
        raise ValueError("Invalid Huffman code length")
    code = 0
    for index, (symbol, length) in enumerate(sorted_items):
        if index:
            code = (code + 1) << (length - prior_length)
        if length <= 0 or length > 255 or code >= (1 << length):
            raise ValueError("Invalid / non-prefix-free code lengths")
        output[symbol] = (code, length)
        prior_length = length
    return output


def build_canonical(data: list[int] | bytes) -> dict[int, tuple[int, int]]:
    counts = Counter(data)
    if not counts:
        return {}
    root = huffman_tree(counts)
    lengths = {symbol: width for symbol, (_, width) in tree_codes(root).items()}
    return canonical_codes(lengths)


def serialize_lengths(codes: dict[int, tuple[int, int]], symbol_width: int) -> bytes:
    if len(codes) > 65535:
        raise ValueError("Too many symbols")
    result = bytearray(struct.pack('>H', len(codes)))
    for symbol in sorted(codes):
        result.extend(int(symbol).to_bytes(symbol_width, 'big'))
        result.append(codes[symbol][1])
    return bytes(result)


def parse_lengths(packet: bytes, cursor: int, symbol_width: int):
    if cursor + 2 > len(packet):
        raise ValueError("Truncated codebook")
    m = struct.unpack_from('>H', packet, cursor)[0]
    cursor += 2
    lengths = {}
    for _ in range(m):
        if cursor + symbol_width + 1 > len(packet):
            raise ValueError("Truncated codebook entries")
        symbol = int.from_bytes(packet[cursor:cursor + symbol_width], 'big')
        length = packet[cursor + symbol_width]
        cursor += symbol_width + 1
        if symbol in lengths:
            raise ValueError("Duplicate codebook symbol")
        lengths[symbol] = length
    return canonical_codes(lengths), cursor


def decode_one(reader: BitReader, codes: dict[int, tuple[int, int]]) -> int:
    if not codes:
        raise ValueError("Attempt to decode with empty table")
    decoding = {(width, bits): sym for sym, (bits, width) in codes.items()}
    maximum = max(width for _, width in codes.values())
    value = 0
    for width in range(1, maximum + 1):
        value = (value << 1) | reader.read(1)
        if (width, value) in decoding:
            return decoding[(width, value)]
    raise ValueError("Invalid Huffman codeword")


def decoder_for(codes: dict[int, tuple[int, int]]):
    """Precompute lookup once rather than per decoded symbol."""
    lookup = {(width, code): sym for sym, (code, width) in codes.items()}
    maximum = max((width for _, width in codes.values()), default=0)

    def get(reader: BitReader) -> int:
        value = 0
        for width in range(1, maximum + 1):
            value = (value << 1) | reader.read(1)
            if (width, value) in lookup:
                return lookup[width, value]
        raise ValueError("Invalid canonical bitstring")
    return get
