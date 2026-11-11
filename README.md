# Problem 8 — Lossless Data Compression (V4)

This is **V4 (P1 corrective release)** of the five-stage Data Structures & Algorithms assignment, based on official Problem 8 (pages 31–34). V3 was **preserved unchanged** in a separate folder. This draft is **not ready for submission** until the team confirms allocation/deadline, provides physically handwritten Q1–Q5 pages, and inserts a real verified GitHub URL.

## What V4 fixes

1. **Q4 literal correctness:** The underscore in the printed problem denotes a **space** at S[11]. Tests, notebook checks and code smoke example now use `b'ABRACADABRA ABRACADABRA'` (ASCII 32). The sixth emitted token is `(7,4,32)`; the original 7-token sequence structure and Q1–Q3 answers are unchanged.
2. **Canonical Huffman metadata:** With a known alphabet order, six codeword lengths are enough to recover the canonical codes for *theoretical Q3*; the payload remains 224 bits. **The actual standalone V4 format** writes `(symbol,length)` pairs plus format and length metadata. It is **not guaranteed smaller** than V3's preorder tree representation. For the pinned 10,000-byte random corpus, V3 = **10,326 B** and V4 = **10,520 B**. Slides and handwritten guide now state this explicitly.
3. **Benchmark reproducibility:** One `benchmark_protocol.py` is used by both notebook and CLI; one authoritative `benchmark_results.csv` with 20 verified rows; SHA-256-pinned input fixtures and `data/dataset_manifest.json`; `benchmark_environment.json` captures CPU/Python/dependency versions, time, clock, counts, and hashes. One warm-up and **five measured runs**, with speed reported as input MiB per **median elapsed seconds**. Each timed iteration is byte-perfect verified. Eight graphs come from the same rows.

## Files

- `HANDWRITTEN_SOLUTION_GUIDE.md` and `.pdf` — corrected **typeset** Q1–Q5 copy-preparation guide. **It is not a physical handwritten submission.**
- `Problem8_Compression_Lab.ipynb` — **executed** Jupyter notebook containing all five codec implementations. The benchmark section additionally imports `benchmark_protocol.py` and requires the supplied `data/` fixtures: **run the notebook from this project folder**.
- `compression_codecs.py` — reusable compressors/decompressors for V1 fixed length, V2 RLE, V3 heap Huffman, V4 canonical Huffman and V5 LZ77+canonical Huffman.
- `benchmark_protocol.py`, `run_benchmarks.py` — one shared benchmark definition and CLI runner.
- `benchmark_results.csv`, `benchmark_environment.json` — current **single-run snapshot**, verified and documented. Rerunning either benchmark entry point regenerates the same packet sizes but new hardware-dependent speed numbers.
- `data/` — byte-exact pinned samples for DNA, real Python source (50 KiB), and 10,000 `os.urandom` bytes; a checksummed JSON manifest. The long-runs dataset is deterministic in code and also checksummed.
- `figures/ratio_{1..4}.png`, `figures/throughput_{1..4}.png` — eight plots from `benchmark_results.csv`. Other legacy chart snapshots are not part of the V4 deliverable.
- `Problem8_Compression_Presentation.pptx`, `.pdf` — refreshed, editable 13-slide presentation and its rendered PDF (still includes clearly marked GitHub/group/deadline placeholders).
- `test_compression.py`, `test_regression_v4.py` — 11 automated tests, including 1,250 varied codec round trips and 4,080 independent LZ77 reference comparisons.
- `V4_CHANGELOG.md`, `V4_VALIDATION.json`, `REVIEW_LOG.md`, `PROJECT_STATE.md`, `REQUIREMENTS.md`, `SUBMISSION_CHECKLIST.md` — review and project control.

## Reproduce results

Python 3.11+ recommended. Dependencies are in `requirements.txt`.

```bash
python -m pip install -r requirements.txt
python -m unittest test_compression.py test_regression_v4.py -v
python run_benchmarks.py             # writes benchmark_results.csv, benchmark_environment.json, 8 charts
python make_notebook.py               # regenerates AND executes the notebook in this folder
node create_slides.js                 # requires npm package pptxgenjs, recreates PPTX from current 8 charts
# Export PPTX to PDF using PowerPoint / LibreOffice, then visually verify.
```

**Important workflow:** `make_notebook.py` re-benchmarks and rewrites the CSV/graphs; regenerate slides *after* the final reference run to keep them synchronized. Always leave the `data` folder intact and do not independently regenerate the random-byte corpus when reproducing this report. CPU timings are **not bit-for-bit reproducible**, unlike hashes, entropy and packet sizes.

### Benchmark corpus (pinned)

1. **Long runs**: 5,000 `A` + 5,000 `B` bytes.
2. **DNA**: 12,000 weighted random nucleotides, `p(A)=0.7`, others 0.1, seeded `Random(20261106)` and stored.
3. **Python source**: 50 KiB snapshot of real installed Python standard-library files, stored unchanged.
4. **Uniform random bytes**: produced with `os.urandom(10000)` **once**, saved unchanged to maintain the same sample across runs.

Plots compare **total compressed packet bits per original input byte** (includes metadata + padding), the raw 8-bit baseline, and zero-order empirical entropy H0. The symbol-by-symbol Shannon lower bound does **not** constrain repeated-phrase LZ77 to H0 bits per byte. V5 is an **educational custom container**, not RFC1951-compatible DEFLATE.

## Still required before submission

- Confirm Problem 8 is actually assigned to the group, along with names, deadline, course and exact accepted file types.
- Physically write Q1–Q5 by hand, scan the pages and inspect them for completeness and legibility.
- Upload the real code and notebook to the group GitHub repository; replace the visible placeholder on slide 13 and verify the link.
- Submit the verified final slides and required handwritten scans according to the professor's actual instructions.

**V4 status:** P1 technical issues corrected and revalidated; **P0 submission items remain open**. See `V4_CHANGELOG.md`.
