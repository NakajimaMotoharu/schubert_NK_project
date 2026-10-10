"""Fresh mapper contract PT, new NativeReader byte; dependencies remain qualified926."""
from pathlib import Path

if __name__=='__main__':
    raw=Path(__file__).with_name('pg1014_stream_selected_v5.py').read_text()
    assert raw.count('pg1014-stream-selected-v5')==1
    raw=raw.replace('pg1014-stream-selected-v5','pg1019-stream-selected-v8').replace('PG1014-stream-selected-v5','PG1019-stream-selected-v8')
    exec(compile(raw,'<PG1019 explicit exception mapper contract>','exec'),{'__name__':'__main__'})
