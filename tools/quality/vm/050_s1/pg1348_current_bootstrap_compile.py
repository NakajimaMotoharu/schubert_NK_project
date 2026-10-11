"""Explicit flat runtime helper ABI; nested old tool test fixtures are not dependencies."""
from pathlib import Path
from pg1346_current_bootstrap_compile import source as previous
R = Path(__file__).resolve().parent

def source():
    raw = previous().replace('pg1345', 'pg1348').replace('Pg1345', 'Pg1348')
    marker = "if name.endswith('.class'):"
    if raw.count(marker) != 1:
        raise ValueError('one flat ABI copy boundary required')
    raw = raw.replace(marker, "if name.endswith('.class') and '/' not in name:")
    compile(raw, '<flat runtime ABI current Bootstrap compiler>', 'exec')
    return raw

if __name__ == '__main__':
    exec(compile(source(), '<new immutable current Bootstrap build>', 'exec'),
         {'__file__': str(R / 'pg1348_current_bootstrap_compile.py'), '__name__': '__main__'})
