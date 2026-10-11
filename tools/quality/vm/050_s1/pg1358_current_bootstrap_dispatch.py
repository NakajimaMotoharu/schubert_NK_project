"""New-only stage/verify/existingADMIN20; old143 and one recovery remain immutable."""
from pathlib import Path
import sys
from pg1349_current_bootstrap_dispatch import source as previous
R = Path(__file__).resolve().parent

def source():
    raw = previous().replace('Pg1348', 'Pg1356').replace('pg1348', 'pg1356')
    marker = "    action=sys.argv[1];assert not subprocess.check_output(['git','status','--porcelain'])"
    if raw.count(marker) != 1:
        raise ValueError('one immutable host dispatch precondition required')
    raw = raw.replace(marker, marker + "\n    assert(W/'pg1355-bootstrap-fixed-handoff-v2.exit').read_bytes()==b'0\\n'\n    assert(W/'pg1348-verify-v3.exit').read_bytes()==b'143\\n'")
    compile(raw, '<new fixed DB application Bootstrap transport>', 'exec')
    return raw

if __name__ == '__main__':
    if sys.argv[1:] not in (['stage'], ['verify'], ['execute']):
        raise ValueError('fixed Bootstrap phase required')
    exec(compile(source(), '<new fixed Bootstrap once dispatch>', 'exec'),
         {'__file__': str(R / 'pg1358_current_bootstrap_dispatch.py'), '__name__': '__main__'})
