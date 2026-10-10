"""Freeze same-source three JAR bytes and Werror physical pin component probe."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from pg1280_held_channel_full_collect import SOURCE,T,W,sha

TARGET=W/'pg1282-physical-pin-tools-v1'


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain'],cwd=T):
        raise ValueError('clean operator required')
    if subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml'],cwd=T):
        raise ValueError('fresh-qualified source must not change')
    run=W/'pg1279-held-channel-six-host-v1'
    qualified=json.loads((run/'manifest.safe.json').read_bytes())
    if qualified['actualExit']!=0 or qualified['candidateSource']!=SOURCE:
        raise ValueError('actual current whole-six qualification required')
    if os.path.lexists(TARGET):raise ValueError('new-only immutable probe required')
    TARGET.mkdir(mode=0o700)
    for module in ['protocol','storage','bootstrap']:
        jar=run/module/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')
        if sha(jar)!=qualified['moduleResults'][module]['jarSha256']:
            raise ValueError('frozen current JAR hash refused')
        shutil.copyfile(jar,TARGET/(module+'.jar'))
    source=Path(__file__).with_name('Pg1282PhysicalPinProbe.java')
    shutil.copyfile(source,TARGET/source.name)
    cp=':'.join(str(TARGET/(m+'.jar'))for m in ['protocol','storage','bootstrap'])
    m2=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    cp+=':'+':'.join(str(m2/p)for p in [
        'com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar',
        'com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar',
        'com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'])
    log=TARGET/'compile.private.log'
    with log.open('xb')as f:
        result=subprocess.run(['/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/javac',
          '-Xlint:all','-Werror','-sourcepath','','-cp',cp,'-d',str(TARGET),str(TARGET/source.name)],stdout=f,stderr=f)
        f.flush();os.fsync(f.fileno())
    hashes={str(p.relative_to(TARGET)):sha(p)for p in TARGET.rglob('*')if p.is_file()}
    safe={'actualExit':result.returncode,'source':SOURCE,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip(),
        'fileHashes':hashes,'frozenFreshSixJarBytes':True,'Werror':True,'formalAccepted':False}
    with(TARGET/'manifest.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    for p in TARGET.rglob('*'):
        if p.is_file():p.chmod(0o400)
    print(json.dumps({k:v for k,v in safe.items()if k!='fileHashes'}))
    return result.returncode


if __name__=='__main__':raise SystemExit(main())
