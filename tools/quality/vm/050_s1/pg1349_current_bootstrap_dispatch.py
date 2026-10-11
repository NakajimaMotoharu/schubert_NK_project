"""Current fixed existingADMIN only; durable one reservation before each dispatch."""
from pathlib import Path
import sys
from pg986_current_bootstrap_native import source as prior
R = Path(__file__).resolve().parent

def source():
    raw = prior()
    for old, new in (
        ('Pg983', 'Pg1348'), ('pg983', 'pg1348'),
        ('PG932', 'PG1292'), ('pg932', 'pg1292'),
        ('cc9ed874-7f4f-450e-a188-8de1e42c8441', 'cbca8738-3b24-4090-b77c-bf029677cdd6'),
        ('pg963-stop-v1.exit', 'pg1336-stop-v1.exit'),
        ('pg968-terminal-final-v1.exit', 'pg1340-published-terminal-post-v4.exit'),
        ('pg960-completed-readonly-v1.safe.json', 'pg1340-published-terminal-post-v4.safe.json'),
        ('40ef6e894573d2ffab1d1732124960f9c98d5f97', '769ddb15cd735c25fef581b5f9850ef9d0053c0f'),
        ('pg978-bootstrap-before-v2', 'pg1344-current-bootstrap-before-v1'),
    ):
        if old not in raw:
            raise ValueError('complete current dispatch binding required: ' + old)
        raw = raw.replace(old, new)
    marker = "    if action=='stage':"
    if raw.count(marker) != 1:
        raise ValueError('one actual transport phase boundary required')
    raw = raw.replace(marker, '''    # Every action is reserved durably before its first external mutation.
    with Path(str(base)+'.requested').open('x') as reservation:
        reservation.write('oneDispatch=true\\n');reservation.flush();os.fsync(reservation.fileno())
    directory=os.open(W,os.O_RDONLY|os.O_DIRECTORY);os.fsync(directory);os.close(directory)
''' + marker)
    compile(raw, '<current once-only Bootstrap dispatcher>', 'exec')
    return raw

if __name__ == '__main__':
    if sys.argv[1:] not in (['stage'], ['verify'], ['execute']):
        raise ValueError('one fixed Bootstrap action required')
    exec(compile(source(), '<current existingADMIN dispatch>', 'exec'),
         {'__file__': str(R / 'pg1349_current_bootstrap_dispatch.py'), '__name__': '__main__'})
