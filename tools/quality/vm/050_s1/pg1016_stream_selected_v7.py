"""Fresh stream fault through actual low-level read path, preserving v6 failed fixture."""
from pathlib import Path

if __name__=='__main__':
    raw=Path(__file__).with_name('pg1014_stream_selected_v5.py').read_text()
    assert raw.count('pg1014-stream-selected-v5')==1
    raw=raw.replace('pg1014-stream-selected-v5','pg1016-stream-selected-v7').replace('PG1014-stream-selected-v5','PG1016-stream-selected-v7')
    exec(compile(raw,'<PG1016 low-level provider fault>','exec'),{'__name__':'__main__'})
