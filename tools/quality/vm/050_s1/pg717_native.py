"""Immutable new tool transport, then distinct verify/activate once; old ops never replayed."""
from pathlib import Path
from pg717_sources import bind
from pg662_sources import replace

R = Path(__file__).resolve().parent


def source():
    raw = bind((R / 'pg685_native.py').read_text())
    raw = replace(raw, (
        ('pg717-frozen-v4.safe.json', 'pg717-frozen-v1.safe.json'),
        ("frozen['graphCases'] == 4", "frozen['graphCases'] == 3"),
        ('pg717-completed-tools-v4', 'pg717-completed-tools-v1'),
        ("files[name] = R/name", "files[name] = W/'pg717-completed-tools-v1'/name if name.startswith('pg717_') else R/name"),
        ("assert (R/'pg717_completed_refs.py').read_text() == profile.refs()", "assert files['pg717_completed_refs.py'].read_text()==profile.refs()"),
    ))
    return raw


if __name__ == '__main__':
    exec(compile(source(), '<current signed completed21 native transport>', 'exec'),
         {'__file__': str(R / 'pg717_native.py'), '__name__': '__main__'})
