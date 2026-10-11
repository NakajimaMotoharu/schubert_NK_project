"""New-only isolated LAN toolchain/source copy, with independent tree hashes."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from lan_server import run, copy

ROOT = Path(__file__).resolve().parents[2]
OUT = Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg1429-lan-environment-v1')
REMOTE = '/home/mini/schubert-nk-pgpt'
HEAD = '2c29d7a17a5eca2f61b24e99af13260a3c286a09'
TOOLCHAIN = Path('/home/mini/codex/project1/work/toolchain')


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        while part := f.read(8 * 1024 * 1024):
            h.update(part)
    return h.hexdigest()


def save(name, value):
    with (OUT / name).open('x') as f:
        json.dump(value, f, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())


def checked(command):
    code, output = run(command, timeout=120)
    if code:
        raise RuntimeError(f'Server command failed: {code}')
    return output.strip()


def main():
    os.umask(0o077)
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == HEAD
    OUT.mkdir(mode=0o700)
    start = time.time()
    checked("python3 -c \"import os; from pathlib import Path; p=Path('"+REMOTE+
        "'); assert not p.exists(); v=os.statvfs('/'); assert v.f_bavail*v.f_frsize > 125*1024**3; "
        "p.mkdir(mode=0o700); [(p/x).mkdir(mode=0o700) for x in ['tools','source','runs','m2','transfer']]\"")
    archive = OUT / 'source.tar'
    with archive.open('xb') as f:
        subprocess.run(['git','archive',HEAD,'src','pom.xml','mvnw','.mvn','program/characterization'],
                       cwd=ROOT, stdout=f, check=True)
    # No server.info, host private key, VM, heap, DB, raw token or arbitrary work tree.
    items = [
        (str(archive), REMOTE+'/transfer/source.tar'),
        (str(TOOLCHAIN/'jdk-25.0.4'), REMOTE+'/tools/'),
        (str(TOOLCHAIN/'m2/wrapper/dists/apache-maven-3.9.12/6068d197')+'/', REMOTE+'/tools/maven/'),
        (str(TOOLCHAIN/'m2/repository')+'/', REMOTE+'/m2/repository/'),
    ]
    for index, (source, destination) in enumerate(items):
        code, output = copy(source, destination)
        save(f'transfer-{index}.safe.json', {'source':source,'destination':destination,'exitCode':code,
                                          'statistics':output})
        if code:
            raise RuntimeError(f'Transfer {index} failed; partial remains private')
    remote_sha = checked("sha256sum "+REMOTE+'/transfer/source.tar').split()[0]
    assert remote_sha == digest(archive)
    checked('tar -xf '+REMOTE+'/transfer/source.tar -C '+REMOTE+'/source')
    version = checked(REMOTE+'/tools/jdk-25.0.4/bin/java -version 2>&1; JAVA_HOME='+
                      REMOTE+'/tools/jdk-25.0.4 '+REMOTE+'/tools/maven/bin/mvn -version')
    save('manifest.safe.json', {'run':'PG1429-LAN-environment','snapshotHead':HEAD,
        'productionSource':'769ddb15cd735c25fef581b5f9850ef9d0053c0f',
        'sourceArchiveSha256':remote_sha,'actualExit':0,'elapsedSeconds':time.time()-start,
        'versions':version,'serverRegion':REMOTE,'serverHostKeyVerified':True,
        'businessActions':0,'vmBootIssued':False,'formalAccepted':False,
        'toolTreeVerificationPending':True,'selectedPtPending':True})
    print(json.dumps({'run':'PG1429','actualExit':0,'elapsedSeconds':time.time()-start,
                      'sourceArchiveSha256':remote_sha,'formalAccepted':False}))


if __name__ == '__main__':
    main()
