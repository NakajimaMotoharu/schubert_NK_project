"""Fixed API-only owner boundary run; no OS admission or old exec reuse."""
from pathlib import Path
import subprocess

R = Path(__file__).resolve().parent
EXTRA = ('dev.codex.schubert.nk.api.file.InspectorOwnerContractTest',
         'dev.codex.schubert.nk.api.maintenance.InspectionRunExecutorTest')


def source():
    raw = (R/'pg669_entry_selected_v1.sh').read_text()
    raw = raw.replace('pg669-entry-component-v1', 'pg676-inspector-owner-component-v3')
    raw = raw.replace('PG669_ENTRY_SELECTED', 'PG676_OWNER_SELECTED')
    raw = raw.replace('InspectorEntryBoundaryTest,',
                      'InspectorOwnerContractTest,InspectionRunExecutorTest,InspectorEntryBoundaryTest,')
    lines = raw.splitlines()
    index = next(i for i, line in enumerate(lines)
                 if line.startswith('  dev.codex.schubert.nk.api.file.InspectorApplicationTest'))
    lines[index:index] = ['  '+name+' '+chr(92) for name in EXTRA]
    assert not any(line.startswith('+') for line in lines)
    for name in EXTRA:
        assert sum(line.strip() == name+' '+chr(92) for line in lines) == 1
        assert name.rsplit('.', 1)[1] in raw.split('-Dtest=', 1)[1].splitlines()[0].split(',')
    return '\n'.join(lines)+'\n'


if __name__ == '__main__':
    fixed = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    raise SystemExit(subprocess.run(['/bin/bash', '-s', '--', fixed], input=source().encode()).returncode)
