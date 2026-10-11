"""Fresh64MiB namespace after fixed failed pair recovery; no old phase replay."""
from pathlib import Path
import sys
from pg1358_current_bootstrap_dispatch import source as previous
R=Path(__file__).resolve().parent

def source():
    raw=previous().replace('Pg1356','Pg1362').replace('pg1356','pg1362')
    marker="    action=sys.argv[1];assert not subprocess.check_output(['git','status','--porcelain'])"
    if raw.count(marker)!=1:raise ValueError('one actual immutable dispatch guard required')
    raw=raw.replace(marker,marker+"\n    assert(W/'pg1361-bootstrap-fixed-pair-handoff-v1.exit').read_bytes()==b'0\\n'\n    assert(W/'pg1356-verify-v3.exit').read_bytes()==b'143\\n'")
    compile(raw,'<current64MiB Bootstrap dispatcher>','exec');return raw

if __name__=='__main__':
    if sys.argv[1:]not in(['stage'],['verify'],['execute']):raise ValueError('fixed Bootstrap action required')
    exec(compile(source(),'<fresh current Bootstrap once dispatch>','exec'),{'__file__':str(R/'pg1364_current_bootstrap_dispatch.py'),'__name__':'__main__'})
