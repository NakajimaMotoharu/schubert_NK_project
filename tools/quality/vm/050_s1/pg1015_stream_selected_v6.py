"""Same qualified dependencies, fresh independent virtual-reader provider failure test."""
if __name__=='__main__':
    # Execute the frozen five profile with a new-only output slot; no old target/run reuse.
    from pathlib import Path
    code=(Path(__file__).with_name('pg1014_stream_selected_v5.py')).read_text()
    assert code.count('pg1014-stream-selected-v5')==1
    code=code.replace('pg1014-stream-selected-v5','pg1015-stream-selected-v6').replace('PG1014-stream-selected-v5','PG1015-stream-selected-v6')
    exec(compile(code,'<PG1015 independent provider outcomes>','exec'),{'__name__':'__main__'})
