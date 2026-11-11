"""Run the exact same benchmark protocol and pinned fixtures as the notebook."""
from benchmark_protocol import load_datasets, run_benchmark, write_benchmark_outputs, render_plots
from compression_codecs import CODECS, lz77_tokens

def execute():
    data=load_datasets()
    rows=run_benchmark(data,CODECS)
    meta=write_benchmark_outputs(rows)
    plots=render_plots(rows)
    trace=lz77_tokens(b'ABRACADABRA ABRACADABRA',12,12)
    assert trace==[(0,0,65),(0,0,66),(0,0,82),(3,1,67),(2,1,68),(7,4,32),(12,10,65)]
    print('PASS:',len(rows),'dataset/codec combinations; charts:',len(plots))
    print('Environment and checksums: benchmark_environment.json')
    return rows

if __name__=='__main__':execute()
