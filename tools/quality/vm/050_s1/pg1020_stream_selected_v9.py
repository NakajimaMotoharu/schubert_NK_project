"""Domain exception value mapper; preserves original exact unknown-failure suppression."""
from pathlib import Path

if __name__=='__main__':
    raw=Path(__file__).with_name('pg1014_stream_selected_v5.py').read_text()
    assert raw.count('pg1014-stream-selected-v5')==1
    raw=raw.replace('pg1014-stream-selected-v5','pg1020-stream-selected-v9').replace('PG1014-stream-selected-v5','PG1020-stream-selected-v9')
    exec(compile(raw,'<PG1020 domain exception mapper>','exec'),{'__name__':'__main__'})
