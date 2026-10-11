"""BUG1107 isolated Unit lookup investigation, no service/VM operations."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

BASE = Path('/home/mini/schubert-nk-pgpt')
OUT = BASE/'runs/PG1465-unit-scope-v1'


def main():
    os.umask(0o077)
    OUT.mkdir(mode=0o700)
    source = BASE/'source-full-PG1461/src/deployment/systemd'
    results = []
    for name, filename in [
        ('schubert-nk-inbox-inspector', 'schubert-nk-inbox-inspector.service'),
        ('schubert-nk-api', 'schubert-nk-api.service.template'),
        ('schubert-nk-web', 'schubert-nk-web.service.template')]:
        directory = OUT/name
        directory.mkdir(mode=0o700)
        original = (source/filename).read_text()
        lines = ['ExecStart=/bin/true' if line.startswith('ExecStart=') else
                 'WorkingDirectory='+str(directory) if line.startswith('WorkingDirectory=') else
                 line for line in original.splitlines()]
        unit = directory/(name+'.service')
        unit.write_text('\n'.join(lines)+'\n')
        for dep in ['postgresql', 'artemis', 'schubert-nk-expiry-cleanup',
                    'schubert-nk-api', 'schubert-nk-web', 'caddy']:
            file = directory/(dep+'.service')
            if file != unit:
                file.write_text('[Service]\nType=oneshot\nExecStart=/bin/true\n')
        for target in ['sysinit', 'basic', 'shutdown']:
            (directory/(target+'.target')).write_text(
                '[Unit]\nDescription=Independent PT dependency stub\nDefaultDependencies=no\n')
        def verify():
            r = subprocess.run(['/usr/bin/systemd-analyze','verify','--man=no',str(unit)],
                env={'SYSTEMD_UNIT_PATH':str(directory),'LC_ALL':'C'},capture_output=True)
            return {'exit':r.returncode,'stdout':r.stdout.decode(), 'stderr':r.stderr.decode()}
        positive = verify()
        # Deliberate project-local invalid directive must remain visible. Do not
        # discard diagnostics or substitute a successful verifier result.
        with unit.open('a') as f:
            f.write('\n[Service]\nNKInvalidDirectiveForNegativeOracle=yes\n')
        negative = verify()
        results.append({'name':name,'inputSha256':hashlib.sha256(original.encode()).hexdigest(),
                        'positive':positive,'negative':negative})
    valid = all(r['positive']=={'exit':0,'stdout':'','stderr':''}
                and 'Unknown key' in r['negative']['stderr']
                and 'NKInvalidDirectiveForNegativeOracle' in r['negative']['stderr']
                for r in results)
    manifest={'run':'PG1465-unit-scope-v1','actualExit':0 if valid else 1,
              'productionSource':'769ddb15cd735c25fef581b5f9850ef9d0053c0f',
              'results':results,'serviceStarted':False,'formalAccepted':False}
    with (OUT/'manifest.safe.json').open('x') as f:
        json.dump(manifest,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(manifest,sort_keys=True))
    return manifest['actualExit']


if __name__=='__main__':raise SystemExit(main())
