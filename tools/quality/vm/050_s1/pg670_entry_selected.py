"""New-only corrective selected run; old43/static1 evidence is immutable."""
from pathlib import Path
import subprocess

R=Path(__file__).resolve().parent
if __name__=='__main__':
    raw=(R/'pg669_entry_selected_v1.sh').read_text()
    assert 'PG669' in raw and 'pg669-entry-component-v1' in raw
    raw=raw.replace('PG669','PG670').replace('pg669-entry-component-v1','pg670-entry-component-v1')
    source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    raise SystemExit(subprocess.run(['/bin/bash','-s','--',source],input=raw.encode()).returncode)
