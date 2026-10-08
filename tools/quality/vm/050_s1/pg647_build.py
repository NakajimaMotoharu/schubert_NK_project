"""New private completed-retirement class; no VM operations."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

R = Path(__file__).resolve().parent
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def java_source():
    value = (R/'Pg635ResumePreparation.java').read_text()
    for old, new in (
        ('Pg635ResumePreparation', 'Pg647RuntimeRetirement'),
        ('pg635-resume-tools-v1', 'pg647-retirement-tools-v1'),
        ('pg635-resume-preparation-v1', 'pg647-runtime-retirement-v1'),
        ('pg635_resume_refs.py', 'pg647_runtime_retirement_refs.py'),
        ('PG635-fixed-resume', 'PG647-runtime-retirement'),
        ('PG635', 'PG647'), ('"prepare"', '"retire"'),
        ('Pg633PendingDeployment.original()', 'Pg642NativeStop.verifyOriginal()'),
        ('onceResumePrepared=true', 'onceResumeRetired=true'),
        ('originalRunCutoffUnchanged=true', 'originalCompletedUnchanged=true'),
        ('RESUME_PREPARED', 'RUNTIME_RETIRED'),
    ):
        assert old in value
        value = value.replace(old, new)
    return value


def main():
    os.umask(0o077)
    assert subprocess.check_output(['git','status','--porcelain'],cwd=R.parents[3]) == b''
    assert (W/'pg646-completed-baseline-v1.exit').read_bytes() == b'0\n'
    target = W/'pg647-retirement-tools-v1'; target.mkdir(mode=0o700)
    java = java_source()
    with (target/'Pg647RuntimeRetirement.java').open('x') as f: f.write(java)
    argument = (R/'Pg635ResumePreparationTest.java').read_text()
    for old, new in (('Pg635ResumePreparationTest','Pg647RuntimeArgumentTest'), ('Pg635ResumePreparation','Pg647RuntimeRetirement'),
                     ('PG635','PG647'), ('"prepare"','"retire"'), ('pg635-resume-tools-v1','pg647-retirement-tools-v1'),
                     ('pg635-resume-preparation-v1','pg647-runtime-retirement-v1')):
        assert old in argument; argument = argument.replace(old,new)
    with (target/'Pg647RuntimeArgumentTest.java').open('x') as f: f.write(argument)
    repo = Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    paths = [W/'pg642-native-tools-v1', W/'pg633-pending-tools-v2', W/'pg498-pending-tools-v3', W/'pg464-code-tools-v2',
             W/'pg490-migration-tools-v4', W/'pg481-pending-tools-v2', W/'pg456-tools-v7']
    host = W/'pg630-retention-factory-six-host-v1'
    for module in ('api','batch','bootstrap','storage','protocol'): paths.append(host/module/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar'))
    paths.extend((W/'pg631-release-v1/api/lib/*', W/'pg631-release-v1/operations/lib/*',
                  repo/'com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar',
                  repo/'com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar',
                  repo/'com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'))
    cp = ':'.join(str(p) for p in paths); j = Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
    with (W/'pg647-compile-v1.private.log').open('xb') as f:
        result = subprocess.run([str(j/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(target),str(target/'Pg647RuntimeRetirement.java'),str(target/'Pg647RuntimeArgumentTest.java')],stdout=f,stderr=f)
    assert result.returncode == 0
    with (W/'pg647-cli-v1.private.log').open('xb') as f:
        result = subprocess.run([str(j/'java'),'-cp',str(target)+':'+cp,'Pg647RuntimeArgumentTest'],stdout=f,stderr=f)
    assert result.returncode == 0
    hashes = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in target.iterdir()}
    with (W/'pg647-build-v1.safe.json').open('x') as f: json.dump({'compileExit':0,'cliExit':0,'files':hashes,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'vmActions0':True},f,sort_keys=True)
    print(json.dumps({'compileExit':0,'cliExit':0,'vmActions0':True}))


if __name__ == '__main__': main()
