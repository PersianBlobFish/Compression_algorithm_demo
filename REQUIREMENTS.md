# Requirements matrix (Phase 1)

**Source**: supplied course assignment text + official *Guided_DSA_Problems-31-34.pdf*, Problem 8, pp.31–34. A missing rubric has not been invented. Completion means a project artifact exists; submission readiness is separate.

| Requirement | Source | Priority | Evidence | Draft status | Verified? |
|---|---|---|---|---|---|
| Assigned problem is Problem 8 | PDF heading / allocation done live | Critical | Explicit group assignment | Assumed for working draft | **No: group allocation unconfirmed** |
| Q1 calculations for V1, V2, entropy and Huffman | Problem Q1 | Critical | Written numeric derivations | Guide prepared | Yes, recomputed |
| Q1 initial + all 5 min-heap merges and final codes | Problem Q1 | Critical | Heap trace and 0/1 tree | Guide prepared | Yes, checked |
| Q2 13-bit decoding + prefix-free reason | Problem Q2 | Critical | 6 manual decode segments | Guide prepared | Yes |
| Q3 canonical reconstruction + 224 bits | Problem Q3 | Critical | Six bitshift derivations | Guide prepared | Yes |
| Q4 LZ77 W=12 L=12, 23 characters | Problem Q4 | Critical | 7 traced triples | Guide prepared | Yes, code tested |
| Q5 5-stage comparison | Problem Q5 | Critical | Time/space/header/skew/phrases | Guide prepared | Yes, conservative bounds |
| **Actual physically handwritten Q1–Q5 pages** | Professor instructions | **Submission blocker** | Readable handwritten scans | Not provided | **No** |
| Implement V1–V5 compress and decompress | Part C | High | Python functions and notebook | Complete | Yes |
| Round trip exact bytes on four specified datasets | Part C | High | 20 exact comparisons | Complete | Yes |
| Graph ratios and 2 speeds for each dataset | Part C | High | 8 bar charts | Complete | Yes |
| Presentation includes algorithm method and results | General assignment | High | 13-slide PPTX/PDF | Draft complete | Visual reviewed |
| GitHub repository holds code | Professor instructions | High | Live repository link | Not yet uploaded | No |
| Real GitHub link appears in slides | Professor instructions | High | Verified URL in exported slides | Placeholder only | No |
| Group details & deadline match assignment | Original assignment | High | Confirmed names and official due date | Unknown | No |

## V4 corrective evidence (2026-11-06)

- **P1 Q4 data fidelity:** actual ASCII space byte at character index 11 in tests, smoke example, runnable notebook and explanatory guide; `(7,4,32)` confirmed — **Verified**.
- **P1 V4 header caveat:** Q3 bit-length-only reconstruction requires pre-agreed symbols/order; physical V4 serializes `(symbol,length)` pairs and can be larger than the physical V3 tree packet — **Verified**.
- **P1 experimental reproducibility:** one shared benchmark harness; exact checksummed datasets (including a fixed os.urandom snapshot); 20 rows, one warm-up, five trials, CPU/Python metadata, eight regenerable plots — **Verified**.
- **Professor-mandated handwritten submission, real GitHub link, group allocation and deadline** — **Not verified / pending**.
