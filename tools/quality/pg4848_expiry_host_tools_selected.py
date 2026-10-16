"""BUG1389 new-only current host PG18.6 identity; do not replay failed4842."""
import hashlib
import os
from pathlib import Path
import subprocess
import pg4842_expiry_audit_selected as previous

PG=Path('/home/mini/codex/project1/work/characterization-tools/root/usr')
WORK=previous.ROOT.parent/'pgpt-runs/PG379/pg4848-expiry-host-tools-selected-v1'


def tools():
    env={**os.environ,'LD_LIBRARY_PATH':str(PG/'lib/x86_64-linux-gnu')+':'+str(PG/'lib/postgresql/18/lib')}
    values={}
    for name in ('initdb','pg_ctl','postgres'):
        path=PG/'lib/postgresql/18/bin'/name
        if not path.is_file():raise ValueError('actual host PostgreSQL program missing')
        result=subprocess.run([str(path),'--version'],env=env,capture_output=True,text=True,timeout=10)
        if result.returncode!=0 or result.stderr or '18.6'not in result.stdout:raise ValueError('actual bounded host PostgreSQL18.6 version required')
        values[name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'version':result.stdout.strip()}
    return values


def source():
    raw=previous.source()
    marker="SCHUBERT_PG_ROOT=str(TOOLCHAIN / 'postgresql18/usr')"
    if raw.count(marker)!=1:raise ValueError('one exact host PG setting boundary')
    raw=raw.replace(marker,'SCHUBERT_PG_ROOT='+repr(str(PG)))
    return raw


def main():
    previous.validate_selection();identity=tools()
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed selected snapshot')
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    ns={**vars(previous.previous.previous.previous.template),'SOURCE':head,'WORK':WORK,'TESTS':list(previous.MODULES),'MODULES':previous.MODULES}
    # Persist environment identity in the original begin receipt, before the first fixture.
    raw=source().replace("'expectedMethods': expected,", "'expectedMethods': expected, 'hostPostgres':"+repr(identity)+',')
    exec(compile(raw,'<current bounded host PG exact selected campaign>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
