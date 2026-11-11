"""Automated unit tests; run `python -m unittest test_compression.py -v`."""
import math
import random
import unittest
from compression_codecs import CODECS, canonical_codes, lz77_tokens, huffman_tree, tree_codes


class CompressionTests(unittest.TestCase):
    def test_all_five_on_edge_cases(self):
        samples = [b'',b'A',b'AAAA',b'ABABABAB',b'ABRACADABRA ABRACADABRA',
                   bytes(range(256)),bytes(range(256))*2,b'\0'*5000+b'X'*5000]
        for name,(encode,decode) in CODECS.items():
            for original in samples:
                with self.subTest(codec=name,length=len(original)):
                    self.assertEqual(decode(encode(original)),original)

    def test_pseudorandom_round_trips(self):
        rng=random.Random(2108)
        for n in [1,2,3,13,127,255,512,1024]:
            original=bytes(rng.randrange(256) for _ in range(n))
            for name,(encode,decode) in CODECS.items():
                with self.subTest(codec=name,length=n):
                    self.assertEqual(decode(encode(original)),original)

    def test_huffman_handworked_lengths_and_bits(self):
        counts={ord(s):c for s,c in {'A':45,'B':13,'C':12,'D':16,'E':9,'F':5}.items()}
        tree=huffman_tree(counts)
        table=tree_codes(tree)
        codes={chr(c):format(bits,f'0{length}b') for c,(bits,length) in table.items()}
        self.assertEqual(codes,{'A':'0','B':'101','C':'100','D':'111','E':'1101','F':'1100'})
        self.assertEqual(sum(counts[byte]*width for byte,(_,width) in table.items()),224)

    def test_canonical_handworked(self):
        lengths={ord(s):length for s,length in [('A',1),('B',3),('C',3),('D',3),('E',4),('F',4)]}
        can=canonical_codes(lengths)
        self.assertEqual({chr(b):format(code,f'0{length}b') for b,(code,length) in can.items()},
                         {'A':'0','B':'100','C':'101','D':'110','E':'1110','F':'1111'})

    def test_lz77_manual_seven_triples(self):
        trace=lz77_tokens(b'ABRACADABRA ABRACADABRA',12,12)
        self.assertEqual(trace,[(0,0,65),(0,0,66),(0,0,82),(3,1,67),
                                (2,1,68),(7,4,32),(12,10,65)])


    def test_q4_literal_byte_is_actual_space(self):
        source = b'ABRACADABRA ABRACADABRA'
        self.assertEqual(len(source), 23)
        self.assertEqual(source[11], 32)   # ASCII SPACE; '_' is display notation only.
        self.assertEqual(lz77_tokens(source, 12, 12)[5], (7, 4, 32))
        for name, (encode, decode) in CODECS.items():
            with self.subTest(codec=name):
                self.assertEqual(decode(encode(source)), source)

    def test_canonical_packet_header_tradeoff(self):
        # Counterexample to the claim that canonical storage is ALWAYS smaller.
        # All 256 possible bytes occur, so explicitly serializing (byte,length)
        # can be more costly than a compact preorder tree.
        all_symbols = bytes(range(256))*20
        tree_len = len(CODECS['V3 Huffman tree'][0](all_symbols))
        canonical_len = len(CODECS['V4 Canonical Huffman'][0](all_symbols))
        self.assertGreater(canonical_len, tree_len)

    def test_shannon_entropy_example(self):
        frequencies=[45,13,12,16,9,5]
        entropy=-sum((n/100)*math.log2(n/100) for n in frequencies)
        self.assertAlmostEqual(entropy,2.219879978107314,places=12)

if __name__=='__main__':unittest.main()
