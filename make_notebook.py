from pathlib import Path
import nbformat as nbf
from nbclient import NotebookClient
BASE=Path(__file__).resolve().parent
source=(BASE/'compression_codecs.py').read_text()
source=source.split("\nif __name__ == '__main__':",1)[0]
anchors=["def v1_fixed_length_compress", "def v3_huffman_tree_compress", "def lz77_tokens", "CODECS = {"]
parts=[]
start=0
for a in anchors:
    next_position=source.index(a)
    parts.append(source[start:next_position])
    start=next_position
parts.append(source[start:])

nb=nbf.v4.new_notebook()
nb.metadata.update({'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}})

def md(s):nb.cells.append(nbf.v4.new_markdown_cell(s))
def code(s):nb.cells.append(nbf.v4.new_code_cell(s))

md('''# Problem 8 — Lossless Data Compression | Executable Lab

**V1 fixed-length → V2 RLE → V3 min-heap Huffman → V4 canonical Huffman → V5 LZ77 + canonical Huffman**

**Group:** [fill in member names]  
**Assignment:** Problem 8, pages 31–34 of the official problem sheet.  
**Method:** implement **both** compress and decompress for every stage; prove exact recovery on 4 datasets; compare compression efficiency and encoding/decoding throughput.

> The five codec implementations are self-contained below; benchmarking additionally uses the supplied `benchmark_protocol.py` and fixed `data/` fixtures. The accompanying `compression_codecs.py` exposes the same functions as a reusable module. The paper calculations are detailed in `HANDWRITTEN_SOLUTION_GUIDE.pdf`; they must be physically reproduced by the student.''')
md('''## Stage prerequisites: bit I/O, Huffman tree, canonical codes

The serializer stores enough header information to decode without relying on an external alphabet. All bitstreams are packed MSB first, with padding bits only in the final byte.''')
code(parts[0])
md('''## V1 — Fixed-length binary encoding and V2 — Run-length encoding

V1 assigns integer IDs to all observed byte values with $b=\\lceil\\log_2(m)\\rceil$ bits (special-case $m=1$: zero-bit codewords are possible because the header stores the data length). V2 uses a 7-bit run length in $[1,127]$ followed by an 8-bit literal. **Theoretical Q1 RLE uses 3 bits per symbol rather than 8**, because that specific example has only six symbols.''')
code(parts[1])
md('''## V3 — Tree-based Huffman and V4 — Canonical Huffman

V3 builds a Huffman tree with `heapq`, writes the tree in preorder, then writes variable-length payload codewords. V4 reconstructs codewords using **lengths and a known ordered alphabet**. In this standalone file format, it serializes each `(symbol, length)` pair and therefore does **not** always outperform a compact explicit Huffman tree header. Both codecs are compared including total metadata. Both handle the empty and one-symbol cases.''')
code(parts[2])
md('''## V5 — LZ77 (W=4096, L=32) + three canonical Huffman tables

The encoder finds the longest valid backward match and emits `(offset, length, next_literal)`. It reserves one final literal for every token. `length=0` means a standalone literal. Huffman coding uses separate canonical tables for length values, nonzero offsets, and next-literal bytes. This is an **educational chained LZ77–canonical-Huffman codec**, not a bit-compatible implementation of the standardized DEFLATE format. Its self-contained packet stores the three sparse codebooks.''')
code(parts[3])
code(parts[4])
md('''## Validate the theoretical hand traces (Q1–Q4)

These executable checks corroborate manual work; they **do not substitute for handwritten traces**.''')
code('''import math

counts = {'A':45, 'B':13, 'C':12, 'D':16, 'E':9, 'F':5}
h = -sum((x/100)*math.log2(x/100) for x in counts.values())
assert abs(h - 2.219879978107314) < 1e-12
assert math.ceil(math.log2(6))*100 == 300
assert 6*10 == 60 and 100*10 == 1000

original_codes = {'A':'0', 'B':'101', 'C':'100', 'D':'111', 'E':'1101', 'F':'1100'}
assert sum(counts[c]*len(code) for c,code in original_codes.items()) == 224
canonical_expected = {'A':'0', 'B':'100', 'C':'101', 'D':'110', 'E':'1110', 'F':'1111'}
canonical_result = canonical_codes({ord(s):len(code) for s,code in original_codes.items()})
assert {chr(s):format(bits,f'0{width}b') for s,(bits,width) in canonical_result.items()} == canonical_expected
bitstream='0101011001110'
reverse={code:s for s,code in original_codes.items()}
decoded='';partial=''
for bit in bitstream:
    partial+=bit
    if partial in reverse:
        decoded+=reverse[partial];partial=''
assert decoded=='ABAFDA' and partial==''
trace=lz77_tokens(b'ABRACADABRA ABRACADABRA',window=12,lookahead=12)
expected=[(0,0,ord('A')),(0,0,ord('B')),(0,0,ord('R')),(3,1,ord('C')),(2,1,ord('D')),(7,4,ord(' ')),(12,10,ord('A'))]
assert trace==expected and trace[5][2] == 32  # ASCII space, never underscore
print(f'Q1 entropy: {h:.6f} bits/symbol; bound: {100*h:.3f} bits; Huffman payload: 224 bits')
print('Q2 decoded 13 bits:', decoded)
print('Q3 canonical codes:',canonical_expected)
print('Q4 7 triples:',[(o,l,chr(c)) for o,l,c in trace])''')
md('''## Extra edge cases (empty messages, all 256 byte values, overlap)

Round-trip verification uses `assert decompress(compress(data)) == data`. The reverse LZ77 copy is performed one byte at a time to support overlapping references.''')
code('''edge_samples = [b'', b'A', b'AAAA', b'ABABABAB', b'A'*5000, bytes(range(256)), bytes(range(256))*2, b'ABRACADABRA ABRACADABRA', bytes([0,255])*100]
for name,(enc,dec) in CODECS.items():
    for original in edge_samples:
        assert dec(enc(original)) == original, (name,len(original))
print(f'Edge-case round trips passed: {len(CODECS)*len(edge_samples)} / {len(CODECS)*len(edge_samples)}')''')
md('''## One reproducible benchmark protocol: exact input files and checksums

1. **Long runs (10,000 bytes)**: `A` repeated 5,000 + `B` repeated 5,000.
2. **Skewed DNA (12,000 bytes)**: a pinned deterministic weighted random draw (seed `20261106`).
3. **Python source (50 KiB)**: a pinned actual Python standard-library source snapshot.
4. **Uniform random bytes (10,000 bytes)**: originally generated using `os.urandom(10000)` and then **saved as a binary fixture** so every rerun sees the *same* random sample.

`data/dataset_manifest.json` provides SHA-256 checksums and generation provenance. The runner and notebook **share** `benchmark_protocol.py` to avoid contradictory CSV snapshots. This notebook is independently executable when run from the complete repository (which includes the dataset fixtures and benchmark utilities). Its codec implementations themselves are embedded above.

> Reproducibility means identical *inputs, compressed packet sizes, entropy and outcomes*. Throughput measurements are **not deterministic** and depend on processor, OS scheduling, Python version and machine load.''')
code('''import hashlib, math
from pathlib import Path
from IPython.display import display, Image
import pandas as pd
from benchmark_protocol import (load_datasets, run_benchmark, write_benchmark_outputs,
                                render_plots, entropy, system_info, WARMUPS, TRIALS)

data_sets=load_datasets()
assert len(data_sets)==4
assert data_sets['Random bytes (10 KB)'].__len__()==10000
print('Pinned test input SHA-256 / entropy:')
for label, data in data_sets.items():
    print(f"{label:26s} {len(data):6,d} bytes  SHA256={hashlib.sha256(data).hexdigest()[:16]}… H0={entropy(data):.4f}")''')
md('''## Exact round-trip verification and unified measurements

Before timing, run one warm-up compress/decompress per codec/dataset, then take **five timed repeats** using `time.perf_counter()`. Report `input MiB / median elapsed seconds`. Validate the output on *every repeat*, including warm-up.

`benchmark_results.csv` is the **single authoritative benchmark CSV** used by the presentation. `benchmark_environment.json` records CPU, Python/dependency versions, clock, trial count, UTC time and fixture hashes. Do not compare timing values from different machines as though they were controlled measurements.''')
code('''rows=run_benchmark(data_sets,CODECS,warmups=WARMUPS,trials=TRIALS,quiet=True)
meta=write_benchmark_outputs(rows)
results=pd.DataFrame(rows)
assert len(results)==20 and results['round_trip'].eq('PASS').all()
display(results[['dataset','codec','packet_bytes','bits_per_byte','h0_bits_per_byte','encode_MiBs','decode_MiBs','round_trip']].round(3))
print('PASS:',len(rows),'exact codec/dataset round trips; unified CSV and metadata written.')
print('CPU:',meta['cpu_model'],'| Python:',meta['python'])''')
md('''## Eight reproducible plotting outputs

All eight figures below derive from the same `rows` table as the presentation. The H0 line is empirical zero-order entropy (not a bound for LZ77). Packet sizes include headers and padding.''')
code('''plots=render_plots(rows)
assert len(plots)==8
for path in plots:
    print(path)
    display(Image(filename=str(path),width=740))''')
code('''for dataset in data_sets:
    subset=results[results['dataset']==dataset]
    best=subset.loc[subset['packet_bytes'].idxmin()]
    print(f"{dataset}: smallest packet = {best['codec']}, {best['bits_per_byte']:.3f} bits/B")
all_symbols=bytes(range(256))*20
v3_size=len(CODECS['V3 Huffman tree'][0](all_symbols))
v4_size=len(CODECS['V4 Canonical Huffman'][0](all_symbols))
assert v4_size>v3_size
print(f'Canonical header counterexample (256 distinct symbols): V3={v3_size} B; V4={v4_size} B')''')
md('''## Interpret results and limitations

- **20/20 tests must pass** on an actual run. Additional edge-case round trips are provided above.
- No codec necessarily wins for every dataset: RLE is suitable for long identical runs; canonical Huffman codes skewed byte frequencies well; LZ77 can exploit repeated *phrases*. Real random bytes are normally incompressible and headers can expand them.
- V5 is **not RFC 1951/DEFLATE compatible**: it demonstrates LZ77 followed by canonical Huffman on length, offset and literal fields using a custom packet header. It also codes short matches (length 1 or 2), sometimes making it worse than plain Huffman on short-alphabet DNA.
- The LZ77 candidate-index implementation retains the full token sequence until the canonical tables are built, hence batch encoder auxiliary storage can be $O(N+W+m')$.
- **Official submission still requires:** physically handwritten solutions for Q1–Q5, verified group assignment and deadline, and the *real* GitHub repository URL in the slides. Do not invent links or pretend a typeset PDF is handwritten.
''')

path=BASE/'Problem8_Compression_Lab.ipynb'
nbf.write(nb,path)
print('Wrote notebook, cells:',len(nb.cells),'path',path)
# Execute all cells in the same folder so saved charts and CSV are generated.
client=NotebookClient(nb,timeout=1200,kernel_name='python3',resources={'metadata':{'path':str(BASE)}})
client.execute()
nbf.write(nb,path)
print('Notebook executed; code cells=',sum(c.cell_type=='code' for c in nb.cells))
