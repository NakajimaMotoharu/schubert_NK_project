"""Fresh current Bootstrap after fixed pair recovery, immutable new namespace."""
from pathlib import Path
from pg1357_current_bootstrap_compile import source as previous
R=Path(__file__).resolve().parent

def source():
    raw=previous().replace('pg1356','pg1362').replace('Pg1356','Pg1362')
    marker=" assert (W/'pg1344-current-bootstrap-before-v1.exit').read_bytes()==b'0\\n'"
    if raw.count(marker)!=1:raise ValueError('one preserved baseline guard required')
    raw=raw.replace(marker,marker+"\n assert (W/'pg1361-bootstrap-fixed-pair-handoff-v1.exit').read_bytes()==b'0\\n'")
    compile(raw,'<fixed whole current compiler>','exec');return raw

if __name__=='__main__':
    exec(compile(source(),'<new current Bootstrap build>','exec'),{'__file__':str(R/'pg1363_current_bootstrap_compile.py'),'__name__':'__main__'})
