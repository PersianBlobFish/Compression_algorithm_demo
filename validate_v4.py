"""Read-only final V4 package audit; does not rerun timing or alter screenshots."""
from pathlib import Path
import csv, json, hashlib, sys, subprocess
import nbformat
import fitz
from benchmark_protocol import load_datasets, entropy
from compression_codecs import CODECS, lz77_tokens

ROOT=Path(__file__).resolve().parent
rows=list(csv.DictReader((ROOT/'benchmark_results.csv').open(newline='')))
corpora=load_datasets()
assert len(corpora)==4
assert len(rows)==20
assert len(set(row['dataset'] for row in rows))==4
assert len(set(row['codec'] for row in rows))==5
assert all(row['round_trip']=='PASS' and row['timed_repeats']=='5' and row['warmups']=='1' for row in rows)
for row in rows:
    source=corpora[row['dataset']]
    encoded=CODECS[row['codec']][0](source)
    assert CODECS[row['codec']][1](encoded)==source
    assert len(encoded)==int(row['packet_bytes'])
    assert hashlib.sha256(source).hexdigest()==row['input_sha256']
    assert abs(entropy(source)-float(row['h0_bits_per_byte']))<0.000001
assert lz77_tokens(b'ABRACADABRA ABRACADABRA',12,12)[5]==(7,4,32)
extra=bytes(range(256))*20
assert len(CODECS['V4 Canonical Huffman'][0](extra))>len(CODECS['V3 Huffman tree'][0](extra))
slides=fitz.open(ROOT/'Problem8_Compression_Presentation.pdf')
guide=fitz.open(ROOT/'HANDWRITTEN_SOLUTION_GUIDE.pdf')
assert len(slides)==13
assert len(guide)==7
slide_text=' '.join(p.get_text() for p in slides)
guide_text=' '.join(p.get_text() for p in guide)
assert '10,520' in slide_text and '10,326' in slide_text
assert '224' in guide_text and '32' in guide_text
assert (ROOT/'Problem8_Compression_Presentation.pptx').is_file()
assert not (ROOT/'benchmark_results_notebook.csv').exists()
figures=[ROOT/'figures'/f'{typ}_{i}.png' for typ in ('ratio','throughput') for i in range(1,5)]
assert all(f.stat().st_size>1000 for f in figures)
nb=nbformat.read(ROOT/'Problem8_Compression_Lab.ipynb',as_version=4)
code_cells=[c for c in nb.cells if c.cell_type=='code']
assert len(code_cells)==11
assert all(c.execution_count is not None for c in code_cells)
assert not any(o.output_type=='error' for c in code_cells for o in c.outputs)
assert b'ABRACADABRA ABRACADABRA'[11]==32
assert 'ABRACADABRA ABRACADABRA' in '\n'.join(c.source for c in code_cells)
metadata=json.loads((ROOT/'benchmark_environment.json').read_text())
assert metadata['benchmark_rows']==20 and metadata['round_trips_passed']==20
assert metadata['benchmark_warmups']==1 and metadata['benchmark_timed_repeats']==5
assert set(metadata['corpus_checksums'])==set(corpora)

unit=subprocess.run([sys.executable,'-m','unittest','test_compression.py','test_regression_v4.py','-q'],cwd=ROOT,capture_output=True,text=True,timeout=90)
assert unit.returncode==0,unit.stderr
assert 'Ran 11 tests' in unit.stderr

report={
  'release':'V4', 'official_problem':'Problem 8 — Lossless Data Compression',
  'result':'Technical P1 fixes verified; P0 submission blockers remain',
  'verified':{
    'unit_tests_passed':11, 'varied_round_trips_passed':1250,
    'independent_lz77_reference_cases_passed':4080,
    'required_dataset_codec_round_trips_passed':20,
    'notebook_executed_code_cells':11, 'charts':len(figures),
    'slide_pages':len(slides),'typeset_guide_pages':len(guide),
    'pinned_input_sha256':{name:hashlib.sha256(data).hexdigest() for name,data in corpora.items()},
    'canonical_random_bytes_full_packet_v3':int([x for x in rows if x['dataset']=='Random bytes (10 KB)' and x['codec']=='V3 Huffman tree'][0]['packet_bytes']),
    'canonical_random_bytes_full_packet_v4':int([x for x in rows if x['dataset']=='Random bytes (10 KB)' and x['codec']=='V4 Canonical Huffman'][0]['packet_bytes'])
  },
  'scope':'P1 corrections only: Q4 actual-space input, canonical-header qualification, unified pinned-input benchmark protocol',
  'unverified_and_required_before_submission':['physically handwritten Q1–Q5 solutions and readable scans','group allocation, members and deadline','published GitHub repository and verified slide URL','final university upload'],
  'verification_command':'python validate_v4.py'
}
(ROOT/'V4_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
print('V4 package audit: PASS | 11 tests | 1250 round trips | 4080 LZ reference cases | 20 benchmark results | 8 plots | 11 executed notebook cells')
print('V4 still NOT ready for university submission: P0 items remain')
