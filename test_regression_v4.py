"""V4 regression: broader byte inputs, exact brute-force LZ77, and benchmark artifacts."""
import csv
import hashlib
import random
import unittest
from pathlib import Path
from benchmark_protocol import load_datasets, entropy
from compression_codecs import CODECS, lz77_tokens

BASE = Path(__file__).resolve().parent


def brute_lz77(data: bytes, window: int, lookahead: int):
    """Independent simple reference using raw original bytes; latest offset breaks ties."""
    output = []
    p = 0
    while p < len(data):
        max_match = min(lookahead, len(data) - p - 1)  # mandatory next literal
        best_length, best_offset = 0, 0
        for j in range(p - 1, max(0, p - window) - 1, -1):
            length = 0
            while length < max_match and data[j + length] == data[p + length]:
                length += 1
            if length > best_length:
                best_length, best_offset = length, p - j
        output.append((best_offset, best_length, data[p + best_length]))
        p += best_length + 1
    return output


class V4Regression(unittest.TestCase):
    def test_1250_varied_round_trips(self):
        rng = random.Random(20261106)
        checked = 0
        for n in range(250):
            if n % 4 == 0:
                data = bytes(rng.randrange(256) for _ in range(n))
            elif n % 4 == 1:
                data = b'A' * n
            elif n % 4 == 2:
                data = bytes([0, 255]) * (n // 2) + bytes([0]) * (n % 2)
            else:
                data = bytes(range(n))
            for codec, (enc, dec) in CODECS.items():
                with self.subTest(codec=codec, length=n):
                    self.assertEqual(dec(enc(data)), data)
                checked += 1
        self.assertEqual(checked, 1250)

    def test_4080_exhaustive_lz77_cases(self):
        checked = 0
        for n in range(8):
            for mask in range(1 << n):
                data = bytes(65 + ((mask >> i) & 1) for i in range(n))
                for w in range(1,5):
                    for l in range(1,5):
                        with self.subTest(data=data, window=w, lookahead=l):
                            self.assertEqual(lz77_tokens(data, w, l), brute_lz77(data, w, l))
                        checked += 1
        self.assertEqual(checked, 4080)

    def test_one_csv_and_fixture_checksums(self):
        corpora = load_datasets()
        with (BASE/'benchmark_results.csv').open(newline='') as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 20)
        self.assertFalse((BASE/'benchmark_results_notebook.csv').exists())
        for row in rows:
            data=corpora[row['dataset']]
            packet=CODECS[row['codec']][0](data)
            self.assertEqual(int(row['packet_bytes']), len(packet))
            self.assertEqual(row['input_sha256'], hashlib.sha256(data).hexdigest())
            self.assertAlmostEqual(float(row['h0_bits_per_byte']), entropy(data), places=5)
            self.assertEqual(row['round_trip'], 'PASS')
            self.assertEqual(row['timed_repeats'], '5')

if __name__ == '__main__': unittest.main(verbosity=2)
