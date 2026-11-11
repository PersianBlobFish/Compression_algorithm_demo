"""Single authoritative, repeatable benchmark harness for both CLI and notebook.

Pinned corpus bytes + SHA256 checksums make output sizes reproducible.
Wall-clock throughput is necessarily system- and load-dependent.
"""
from __future__ import annotations
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import statistics
import sys
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / 'data' / 'dataset_manifest.json'
WARMUPS = 1
TRIALS = 5


def load_datasets(root: Path = ROOT) -> dict[str, bytes]:
    manifest=json.loads((root/'data'/'dataset_manifest.json').read_text())
    result={}
    for item in manifest['datasets']:
        data=(b'A'*5000+b'B'*5000) if 'file' not in item else (root/'data'/item['file']).read_bytes()
        if len(data)!=item['bytes'] or hashlib.sha256(data).hexdigest()!=item['sha256']:
            raise RuntimeError('Pinned corpus checksum mismatch: '+item['name'])
        result[item['name']]=data
    if len(result)!=4:
        raise RuntimeError('Expected the four official datasets')
    return result


def entropy(data:bytes)->float:
    if not data:return 0.0
    return -sum((v/len(data))*math.log2(v/len(data)) for v in Counter(data).values())


def system_info() -> dict:
    try:
        import importlib.metadata as metadata
        packages={p:metadata.version(p) for p in ('matplotlib','numpy','pandas','nbclient','nbformat')}
    except Exception:
        packages={}
    cpu=platform.processor() or platform.uname().processor or 'unavailable'
    try:
        for line in Path('/proc/cpuinfo').read_text().splitlines():
            if line.lower().startswith('model name'):
                cpu=line.split(':',1)[1].strip();break
    except (OSError,ValueError): pass
    return {'utc_timestamp':datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'host_platform':platform.platform(),'python':sys.version.split()[0],
            'cpu_model':cpu,'logical_cores':os.cpu_count(),
            'dependency_versions':packages,'benchmark_warmups':WARMUPS,
            'benchmark_timed_repeats':TRIALS,
            'clock':'time.perf_counter()','timing_aggregation':'median wall-clock seconds',
            'throughput_units':'MiB/s (input MiB / elapsed wall-clock sec)',
            'corpus_manifest':'data/dataset_manifest.json',
            'corpus_checksums':{item['name']:item['sha256'] for item in json.loads(MANIFEST.read_text())['datasets']},
            'note':'Input bytes and packet sizes are reproducible. Speed values will vary by CPU and system load.'}


def run_benchmark(datasets:dict[str,bytes],codecs:dict, warmups:int=WARMUPS, trials:int=TRIALS, quiet:bool=False):
    if trials<1 or warmups<0:raise ValueError('Invalid repeats')
    rows=[]
    for name, source in datasets.items():
        for codec_name,(encode,decode) in codecs.items():
            for _ in range(warmups):
                packet=encode(source)
                if decode(packet)!=source:raise AssertionError((name,codec_name,'warmup mismatch'))
            times_enc=[];times_dec=[]
            for _ in range(trials):
                t0=time.perf_counter()
                packet=encode(source)
                t1=time.perf_counter()
                recovered=decode(packet)
                t2=time.perf_counter()
                if recovered!=source:raise AssertionError((name,codec_name,'round-trip mismatch'))
                times_enc.append(t1-t0);times_dec.append(t2-t1)
            enc_seconds=statistics.median(times_enc)
            dec_seconds=statistics.median(times_dec)
            row={'dataset':name,'bytes':len(source),'input_sha256':hashlib.sha256(source).hexdigest(),
                 'h0_bits_per_byte':round(entropy(source),6),
                 'codec':codec_name,'packet_bytes':len(packet),
                 'bits_per_byte':round(8*len(packet)/len(source),6),
                 'compression_ratio':round(len(source)/len(packet),6),
                 'encode_MiBs':round((len(source)/(1024*1024))/enc_seconds,6),
                 'decode_MiBs':round((len(source)/(1024*1024))/dec_seconds,6),
                 'warmups':warmups,'timed_repeats':trials,'round_trip':'PASS'}
            rows.append(row)
            if not quiet:print(f'{name:24s} {codec_name:23s} {row["bits_per_byte"]:6.3f} bits/B  '
                                f'enc={row["encode_MiBs"]:7.3f} MiB/s dec={row["decode_MiBs"]:7.3f} MiB/s',flush=True)
    if len(rows)!=20 or any(r['round_trip']!='PASS' for r in rows):
        raise AssertionError('Expected exactly 20 successful round-trip results')
    return rows


def write_benchmark_outputs(rows:list[dict], root:Path=ROOT) -> dict:
    root.mkdir(parents=True,exist_ok=True)
    path=root/'benchmark_results.csv'
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    meta=system_info()
    meta['benchmarks_file']=path.name
    meta['round_trips_passed']=sum(x['round_trip']=='PASS' for x in rows)
    meta['benchmark_rows']=len(rows)
    (root/'benchmark_environment.json').write_text(json.dumps(meta,indent=2)+'\n')
    return meta


def render_plots(rows:list[dict], root:Path=ROOT) -> list[Path]:
    figdir=root/'figures';figdir.mkdir(exist_ok=True)
    compact=['Fixed','RLE','Huff tree','Canonical','LZ77+Huff']
    colors=['#78869f','#6e8ab4','#5b63b9','#7c4fc2','#196f86']
    paths=[]
    for index,name in enumerate(dict.fromkeys(r['dataset'] for r in rows),start=1):
        sub=[r for r in rows if r['dataset']==name]
        h0=sub[0]['h0_bits_per_byte']
        fig,ax=plt.subplots(figsize=(10,5))
        bars=ax.bar(compact,[r['bits_per_byte'] for r in sub],color=colors)
        ax.axhline(8.0,color='#374151',linestyle='--',linewidth=1.5,label='Raw = 8 bits/B')
        ax.axhline(h0,color='#d35c60',linestyle=':',linewidth=2,label=f'H0 = {h0:.3f}')
        ax.set_ylabel('Complete packet bits / original byte')
        ax.set_title(name+' | header-inclusive compression')
        ax.legend(fontsize=9)
        ax.set_ylim(bottom=0)
        for b in bars:
            ax.annotate(f'{b.get_height():.2f}',(b.get_x()+b.get_width()/2,b.get_height()),
                        xytext=(0,3),textcoords='offset points',ha='center',fontsize=9)
        fig.tight_layout()
        path=figdir/f'ratio_{index}.png';fig.savefig(path,dpi=170);paths.append(path);plt.close(fig)
        fig,ax=plt.subplots(figsize=(10,5))
        x=np.arange(5)
        ax.bar(x-.19,[r['encode_MiBs'] for r in sub],width=.38,label='Encode',color='#6a5bd0')
        ax.bar(x+.19,[r['decode_MiBs'] for r in sub],width=.38,label='Decode',color='#20918d')
        ax.set_xticks(x,compact)
        ax.set_ylabel(f'Throughput (MiB/s, median of {sub[0]["timed_repeats"]} timed runs)')
        ax.set_title(name+' | measured Python throughput')
        ax.legend(fontsize=9)
        fig.tight_layout()
        path=figdir/f'throughput_{index}.png';fig.savefig(path,dpi=170);paths.append(path);plt.close(fig)
    return paths
