"""Fresh immutable current769 ABI/compiler; no guest mutations."""
from pathlib import Path
from pg985_current_bootstrap_compile import source as prior
R = Path(__file__).resolve().parent

def source():
    code = prior()
    changes = (
        ('from pg983_current_bootstrap_sources import files,SOURCE', 'from pg1345_current_bootstrap_sources import files,SOURCE'),
        ('pg984_current_bootstrap_sources_test.py', 'pg1345_current_bootstrap_sources_test.py'),
        ('Pg983', 'Pg1345'), ('pg983', 'pg1345'),
        ('pg978-bootstrap-before-v2', 'pg1344-current-bootstrap-before-v1'),
        ('pg932-release-v1', 'pg1292-release-v1'),
        ('pg864-completed-tools-v3', 'pg1334-native-tools-v1'),
        ('pg864-frozen-v3.safe.json', 'pg1335-frozen-v1.safe.json'),
    )
    for old, new in changes:
        if old not in code:
            raise ValueError('complete host current ABI binding required: ' + old)
        code = code.replace(old, new)
    compile(code, '<current source Bootstrap compiler>', 'exec')
    return code

if __name__ == '__main__':
    exec(compile(source(), '<current Bootstrap build>', 'exec'),
         {'__file__': str(R / 'pg1346_current_bootstrap_compile.py'), '__name__': '__main__'})
