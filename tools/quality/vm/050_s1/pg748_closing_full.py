"""451 fresh full-six trigger: SSC234 shared checkpoint/profile/export and two entry changes."""
from pathlib import Path
import subprocess
from pg713_full import source as previous

R=Path(__file__).resolve().parent


def source():
    raw=previous();assert raw.count('pg713-expiry-six-host-v1')==1
    return raw.replace('pg713-expiry-six-host-v1','pg748-closing-six-host-v1').replace('PG713_FULL','PG748_FULL')


if __name__=='__main__':
    fixed=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    raise SystemExit(subprocess.run(['/bin/bash','-s','--',fixed],input=source().encode()).returncode)
