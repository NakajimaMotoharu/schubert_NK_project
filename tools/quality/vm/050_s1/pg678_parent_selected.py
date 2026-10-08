"""One fresh bootstrap parent-observation group, no JVM/native ownership claims."""
from pathlib import Path
import subprocess

R = Path(__file__).resolve().parent
CASES = ('MaintenanceParentGuardTest', 'MaintenanceOwnerFrameTest', 'ChildStartupContextTest')


def source():
    raw = (R/'pg669_entry_selected_v1.sh').read_text()
    raw = raw.replace('pg669-entry-component-v1', 'pg678-parent-guard-component-v1')
    raw = raw.replace('PG669_ENTRY_SELECTED', 'PG678_PARENT_SELECTED')
    raw = raw.replace('src/schubert-nk-api', 'src/schubert-nk-bootstrap')
    raw = raw.replace('api.exec', 'bootstrap.exec').replace('schubert-nk-api-', 'schubert-nk-bootstrap-')
    lines = raw.splitlines()
    command = next(i for i, line in enumerate(lines) if '-Dtest=' in line)
    lines[command] = lines[command].split('-Dtest=')[0]+'-Dtest='+','.join(CASES)
    first = next(i for i, line in enumerate(lines) if line.startswith('for task_class in '))
    last = next(i for i in range(first, len(lines)) if lines[i].endswith('; do'))
    names = ['dev.codex.schubert.nk.bootstrap.'+name for name in CASES]
    lines[first:last+1] = ['for task_class in '+' '.join(names)+'; do']
    assert not any(line.startswith('+') for line in lines)
    assert len(set(names)) == 3 and all(name.rsplit('.', 1)[1] in lines[command] for name in names)
    return '\n'.join(lines)+'\n'


if __name__ == '__main__':
    fixed = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    raise SystemExit(subprocess.run(['/bin/bash', '-s', '--', fixed], input=source().encode()).returncode)
