from __future__ import annotations

from collections import defaultdict, deque
import struct

from ._shared import (BitReader, BitWriter, build_canonical, decoder_for,
                      parse_lengths, serialize_lengths)


def lz77_tokens(data: bytes, window: int = 4096, lookahead: int = 32):
    """Longest-match LZ77 triples (offset,length,next_literal).

    Full exact search of matching three-byte-prefix candidate positions in the
    previous W bytes; matching from 1 or 2 bytes uses last seen positions.
    Supports overlapping back-references and consumes a final literal always.
    """
    if window < 1 or lookahead < 1:
        raise ValueError('Window and lookahead must be positive')
    n = len(data)
    p = 0
    indexed_until = 0
    expired_until = 0
    trigrams = defaultdict(deque)
    last_one = {}
    last_two = {}
    output = []
    while p < n:
        # Add all positions processed by preceding token, even if referenced.
        while indexed_until < p:
            j = indexed_until
            last_one[data[j]] = j
            if j + 2 <= n:
                last_two[data[j:j+2]] = j
            if j + 3 <= n:
                trigrams[data[j:j+3]].append(j)
            indexed_until += 1
        # Maintain only positions starting in S[max(0,p-W)..p-1].
        oldest_valid = max(0, p-window)
        while expired_until < oldest_valid:
            j = expired_until
            if j + 3 <= n:
                key = data[j:j+3]
                positions = trigrams.get(key)
                if positions and positions[0] == j:
                    positions.popleft()
                    if not positions:
                        del trigrams[key]
            expired_until += 1
        maximum = min(lookahead, n-p-1)  # reserve a final next_char
        best_len = 0
        best_off = 0
        if maximum >= 3:
            for j in reversed(trigrams.get(data[p:p+3], ())):
                if j < oldest_valid:
                    break
                length = 3
                while length < maximum and data[j+length] == data[p+length]:
                    length += 1
                if length > best_len:
                    best_len, best_off = length, p-j
                if best_len == maximum:
                    break
        if best_len < 2 and maximum >= 2:
            j = last_two.get(data[p:p+2], -1)
            if oldest_valid <= j < p:
                best_len, best_off = 2, p-j
        if best_len < 1 and maximum >= 1:
            j = last_one.get(data[p], -1)
            if oldest_valid <= j < p:
                best_len, best_off = 1, p-j
        output.append((best_off, best_len, data[p+best_len]))
        p += best_len + 1
    return output


def v5_lz77_deflate_compress(data: bytes) -> bytes:
    tokens = lz77_tokens(data, window=4096, lookahead=32)
    # Three independently canonical-Huffman-coded streams. A length of zero
    # designates a literal; a positive length is followed by a coded offset.
    lengths = [length for _, length, _ in tokens]
    offsets = [offset for offset, length, _ in tokens if length]
    literals = [literal for _, _, literal in tokens]
    length_codes = build_canonical(lengths)
    offset_codes = build_canonical(offsets)
    literal_codes = build_canonical(literals)
    writer = BitWriter()
    for offset, length, literal in tokens:
        writer.write(*length_codes[length])
        if length:
            writer.write(*offset_codes[offset])
        writer.write(*literal_codes[literal])
    header = (b'LZ05' + struct.pack('>II', len(data), len(tokens)) +
              serialize_lengths(length_codes, 1) +
              serialize_lengths(offset_codes, 2) +
              serialize_lengths(literal_codes, 1))
    return header + writer.finish()


def v5_lz77_deflate_decompress(packet: bytes) -> bytes:
    if len(packet) < 12 or packet[:4] != b'LZ05':
        raise ValueError('Invalid LZ77+Huffman packet')
    n, token_count = struct.unpack_from('>II', packet, 4)
    length_codes, cursor = parse_lengths(packet, 12, 1)
    offset_codes, cursor = parse_lengths(packet, cursor, 2)
    literal_codes, cursor = parse_lengths(packet, cursor, 1)
    get_length = decoder_for(length_codes)
    get_offset = decoder_for(offset_codes)
    get_literal = decoder_for(literal_codes)
    reader = BitReader(packet[cursor:])
    result = bytearray()
    for _ in range(token_count):
        length = get_length(reader)
        if length:
            offset = get_offset(reader)
            if not 1 <= length <= 32 or not 1 <= offset <= min(4096, len(result)):
                raise ValueError('Invalid LZ77 reference')
            for _ in range(length):
                result.append(result[-offset])  # overlap is intentionally legal
        result.append(get_literal(reader))
        if len(result) > n:
            raise ValueError('Output exceeds declared uncompressed size')
    if len(result) != n:
        raise ValueError('Incorrect LZ77 output size')
    return bytes(result)
