"""Immutable Werror/currentPG750 ABI + independent fixed failed recovery tests; no VM."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg778_sources as p
from pg777_failure_full import REFERENCE

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
JDK=Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
DEPENDENCIES=('pg491-pending-tools-v1','pg490-migration-tools-v4','pg481-native-tools-v3','pg481-pending-tools-v2','pg456-tools-v7','pg461-known30-tool-v3')


def main():
    os.umask(0o077);assert not subprocess.check_output(['git','status','--porcelain'])
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    assert (W/'pg777-failure-full758-v1.exit').read_text()=='0\n'
    subprocess.run(['python3','-B',str(R/'pg778_contract_test.py')],check=True)
    target=W/'pg778-failed758-tools-v1';target.mkdir(mode=0o700)
    for directory in DEPENDENCIES:
        for old in (W/directory).glob('*.class'):
            new=target/old.name
            # Use the same deterministic ordered classpath as the tested old496 ABI.
            # Later duplicate implementations are not added to this immutable flat payload.
            if not new.exists():
                with new.open('xb')as f:os.fchmod(f.fileno(),0o400);f.write(old.read_bytes())
    sources={'Pg778FailedRecovery.java':p.java(),'Pg778FailedRecoveryTest.java':(R/'Pg778FailedRecoveryTest.java').read_text(),
             'pg778_owned.py':p.helper(),'pg778_refs.py':(R/'pg778_refs.py').read_text(),'pg777_reference_capability.py':REFERENCE}
    for name in ('pg481_native_owned_stop.py','pg480_backup_refs.py','pg466_term_witness.py','pg471_native_term_witness.py'):
        sources[name]=(R/name).read_text()
    for name,raw in sources.items():
        with(target/name).open('x')as f:os.fchmod(f.fileno(),0o400);f.write(raw);f.flush();os.fsync(f.fileno())
    release=W/'pg750-release-v1'
    libs=[str(target),str(release/'api/api.jar'),str(release/'operations/batch.jar'),str(release/'api/lib/*'),str(release/'operations/lib/*')]
    annotations=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    libs.extend(str(annotations/x)for x in ('com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar','com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar','com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'))
    cp=':'.join(libs);started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    for phase,args in [('compile',[str(JDK/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(target),str(target/'Pg778FailedRecovery.java'),str(target/'Pg778FailedRecoveryTest.java')]),
                       ('oracle',[str(JDK/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg778FailedRecoveryTest'])]:
        log=W/('pg778-'+phase+'-v1.private.log')
        with log.open('xb')as f:r=subprocess.run(args,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
        with(W/('pg778-'+phase+'-v1.exit')).open('x')as f:f.write(str(r.returncode)+'\n')
        if r.returncode:
            print(json.dumps({'phase':phase,'actualExit':r.returncode,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest()}));raise SystemExit(r.returncode)
    files={f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in target.iterdir()}
    for f in target.iterdir():f.chmod(0o400)
    with(target/'payload-sha256.json').open('x')as f:os.fchmod(f.fileno(),0o400);json.dump(files,f,sort_keys=True)
    assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==head and not subprocess.check_output(['git','status','--porcelain'])
    safe={'actualExit':0,'operatorSource':head,'productionSource':p.SOURCE,'manifestSha256':p.DIGEST,'snapshotSha256':'80594db5e3a5588a26b05be729e80a40f750a44230f34c3e025f923f365ddba4',
          'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'fileHashes':files,'pythonIndependentAssertions':151,'javaOracleLogSha256':hashlib.sha256((W/'pg778-oracle-v1.private.log').read_bytes()).hexdigest(),'guestMutation0':True,'formalAccepted':False}
    with(W/'pg778-frozen-v1.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
    print(json.dumps({'actualExit':0,'Werror0':True,'oracle0':True,'pythonAssertions':151,'guestActions0':True,'operatorSource':head}))


if __name__=='__main__':main()
