"""New PG715 ordinary noargs one-shot; no reuse of completed8633."""
from pathlib import Path
from pg690_fresh_parent import source as previous
from pg662_sources import replace

R = Path(__file__).resolve().parent


def source():
    return replace(previous(), (
        ('pg690', 'pg722'), ('pg691', 'pg723'), ('pg689', 'pg721'),
        ('PG682', 'PG715'), ('pg685-completed-activate-v1', 'pg717-completed-activate-v1'),
        ('f69b52ee024ca670723d077dd34b20a2f62803f6575e4ba02d886d395f124187',
         '3849806f2d462004c9135ed29b914388bf17d903219a2dc65a73bf23764eed7a'),
        ('9bd50536f692610036a0ed8b83e0a8b35fe2a66f', '1ec19782a1afe22d1de75b05f4cd12b8a8a8a172'),
        ('076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480',
         '74d35361865a32a6b992f93d78d42844e20a5bb286fa4fc4b5e74520fa6305d5'),
        ('==514', '==524'), ("'originalBatchRows':514", "'originalBatchRows':524"),
        ("'priorBatchRows':514", "'priorBatchRows':524"),
        ("'priorTodayRuns':32", "'priorTodayRuns':42"),
        ("'priorToday32HistoryVerified':True", "'priorToday42HistoryVerified':True"),
    ))


if __name__ == '__main__':
    exec(compile(source(), '<new PG715 ordinary campaign>', 'exec'),
         {'__file__': str(R / 'pg722_fresh_parent.py'), '__name__': '__main__'})
