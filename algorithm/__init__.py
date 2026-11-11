"""Public API for the five modular compression algorithms."""

from ._shared import canonical_codes, huffman_tree, tree_codes
from .v1_fixed_length import v1_fixed_length_compress, v1_fixed_length_decompress
from .v2_rle import v2_rle_compress, v2_rle_decompress
from .v3_huffman_tree import v3_huffman_tree_compress, v3_huffman_tree_decompress
from .v4_huffman_canonical import (
    v4_huffman_canonical_compress, v4_huffman_canonical_decompress,
)
from .v5_lz77_deflate import (
    lz77_tokens, v5_lz77_deflate_compress, v5_lz77_deflate_decompress,
)

CODECS = {
    'V1 Fixed-length': (v1_fixed_length_compress, v1_fixed_length_decompress),
    'V2 RLE': (v2_rle_compress, v2_rle_decompress),
    'V3 Huffman tree': (v3_huffman_tree_compress, v3_huffman_tree_decompress),
    'V4 Canonical Huffman': (v4_huffman_canonical_compress, v4_huffman_canonical_decompress),
    'V5 LZ77 + Canonical': (v5_lz77_deflate_compress, v5_lz77_deflate_decompress),
}

__all__ = [
    'CODECS', 'canonical_codes', 'huffman_tree', 'tree_codes', 'lz77_tokens',
    'v1_fixed_length_compress', 'v1_fixed_length_decompress',
    'v2_rle_compress', 'v2_rle_decompress',
    'v3_huffman_tree_compress', 'v3_huffman_tree_decompress',
    'v4_huffman_canonical_compress', 'v4_huffman_canonical_decompress',
    'v5_lz77_deflate_compress', 'v5_lz77_deflate_decompress',
]
