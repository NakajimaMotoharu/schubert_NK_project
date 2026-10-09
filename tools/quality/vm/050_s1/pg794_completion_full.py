"""451 trigger: same owner completion evidence/orchestration requires fresh six module run."""
import subprocess
from pg748_closing_full import source as prior


def source():
    raw=prior();assert raw.count('pg748-closing-six-host-v1')==1
    return raw.replace('pg748-closing-six-host-v1','pg794-completion-six-host-v1').replace('PG748_FULL','PG794_FULL')


if __name__=='__main__':
    fixed=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    raise SystemExit(subprocess.run(['/bin/bash','-s','--',fixed],input=source().encode()).returncode)
