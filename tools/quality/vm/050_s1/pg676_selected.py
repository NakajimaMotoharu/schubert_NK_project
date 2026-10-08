"""Fixed API-only Inspector owner boundary run; no native admission or old exec reuse."""
from pathlib import Path
import subprocess

R = Path(__file__).resolve().parent


def source():
    raw = (R/'pg669_entry_selected_v1.sh').read_text()
    raw = raw.replace('pg669-entry-component-v1', 'pg676-inspector-owner-component-v1')
    raw = raw.replace('PG669_ENTRY_SELECTED', 'PG676_OWNER_SELECTED')
    raw = raw.replace('InspectorEntryBoundaryTest,', 'InspectorOwnerContractTest,InspectorEntryBoundaryTest,')
    raw = raw.replace('  dev.codex.schubert.nk.api.file.InspectorApplicationTest',
                      '  dev.codex.schubert.nk.api.file.InspectorOwnerContractTest \\\n+  dev.codex.schubert.nk.api.file.InspectorApplicationTest')
    assert raw.count('InspectorOwnerContractTest') == 2
    return raw


if __name__ == '__main__':
    fixed = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    raise SystemExit(subprocess.run(['/bin/bash', '-s', '--', fixed], input=source().encode()).returncode)
