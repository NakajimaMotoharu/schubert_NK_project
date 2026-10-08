"""BUG913 fixed six-NK reactor; fresh v2 only, old resolution failure preserved."""
from pathlib import Path
import subprocess

R=Path(__file__).resolve().parent


def source():
    raw=(R/'pg672_full_v1.sh').read_text()
    assert 'pg672-entry-six-host-v1' in raw and ' clean spotless:check' in raw
    return raw.replace('pg672-entry-six-host-v1','pg672-entry-six-host-v2').replace(' clean spotless:check',
        ' -pl src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api,src/schubert-nk-web,src/schubert-nk-batch clean spotless:check')


if __name__=='__main__':
    fixed=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    raise SystemExit(subprocess.run(['/bin/bash','-s','--',fixed],input=source().encode()).returncode)
