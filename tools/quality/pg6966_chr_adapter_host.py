"""One new-only, offline local run of five public common-harness suites.

No Current/native/Root test or service is executed. Original baseline stays read-only.
Actual child exit is persisted before XML/counter semantic interpretation.
"""
import datetime
import json
import os
import subprocess
import tarfile
from pathlib import Path

from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6958_recovery_catalog import SOURCE, require

SLOT = W/'pg6966-chr-adapter-host-v1'
SELECTED = ('ArtifactComparatorTest','GateCliTest','GateContractTest',
            'GateContractValidatorNegativeTest','TargetAdapterTest')
TC = ROOT.parent/'toolchain'


def write(path, value):
    with path.open('x') as stream:
        json.dump(value,stream,sort_keys=True,indent=2,ensure_ascii=False)
        stream.write('\n');stream.flush();os.fsync(stream.fileno())


def inventory(root):
    return {str(p.relative_to(root)):sha(p) for p in sorted(root.rglob('*')) if p.is_file()}


def safe_extract(archive, destination):
    with tarfile.open(archive) as source:
        for entry in source.getmembers():
            path = Path(entry.name)
            require(not path.is_absolute() and '..' not in path.parts
                    and (entry.isfile() or entry.isdir()), 'regular fixed public archive entries only')
        source.extractall(destination,filter='data')


def main(slot=SLOT, format_files=(), source=SOURCE):
    os.umask(0o077)
    require(not slot.exists(), 'new-only job; existing begin or terminal must be observed, never restarted')
    subprocess.run(['git','diff','--exit-code',source,'--','src','pom.xml','.mvn','mvnw','program/characterization'],
                   cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
    original_baseline = ROOT/'program/characterization/baseline/current'
    before = inventory(original_baseline)
    require(before, 'nonempty original immutable baseline')
    slot.mkdir()
    archive = slot/'source.tar'
    paths = ['pom.xml','.mvn','mvnw','program/characterization',
             *['src/schubert-nk-'+m+'/pom.xml' for m in ('protocol','storage','bootstrap','api','web','batch')]]
    with archive.open('xb') as stream:
        subprocess.run(['git','archive','--format=tar',source,*paths],cwd=ROOT,stdout=stream,check=True)
    snapshot = slot/'snapshot';snapshot.mkdir();safe_extract(archive,snapshot)
    require(inventory(snapshot/'program/characterization/baseline/current') == before,
            'snapshot baseline equals preserved original')
    source_inputs = inventory(snapshot)
    command = [str(TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-o','--no-transfer-progress',
               '-Dmaven.repo.local='+str(TC/'m2/repository'),'-pl','program/characterization',
               '-Dtest='+','.join(SELECTED),
               *(['-DspotlessFiles='+','.join(format_files)] if format_files else []),'verify']
    env = {'PATH':str(TC/'jdk-25.0.4/bin')+':/usr/bin:/bin','JAVA_HOME':str(TC/'jdk-25.0.4'),
           'MAVEN_USER_HOME':str(TC/'m2'),'MAVEN_SKIP_RC':'true','LANG':'C.UTF-8',
           'MAVEN_OPTS':'-Xmx2g -Djava.awt.headless=true'}
    begin = dict(source=source,operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                 branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
                 startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),command=command,
                 cwd=str(snapshot),archiveSha256=sha(archive),inputHashes=source_inputs,
                 originalBaselineHashes=before,selectedSuites=list(SELECTED),toolSha256=sha(Path(__file__)),
                 formatFiles=list(format_files),
                 actualVmActions=0,actualDatabaseActions=0,nativeTestsSelected=0,original4222Replayed=False)
    write(slot/'begin.safe.json',begin)
    with (slot/'maven.log').open('xb') as log:
        child = subprocess.Popen(command,cwd=snapshot,env=env,stdout=log,stderr=subprocess.STDOUT)
        write(slot/'process.safe.json',dict(pid=child.pid,startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                          source=source,command=command,cwd=str(snapshot)))
        code = child.wait()
        log.flush();os.fsync(log.fileno())
    # Unknown or nonzero is preserved as such, before any semantic gate.
    result = dict(source=source,beginSha256=sha(slot/'begin.safe.json'),actualExit=code,
                  endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),logSha256=sha(slot/'maven.log'))
    write(slot/'exit.safe.json',result)
    after = inventory(original_baseline)
    snap_after = {p:sha(snapshot/p) for p in source_inputs}
    result.update(originalBaselineUnchanged=after==before,snapshotInputsUnchanged=snap_after==source_inputs,
                  selectedSuites=list(SELECTED),status='RAW_TERMINAL_ONLY_INDEPENDENT_QUALIFICATION_PENDING')
    write(slot/'manifest.safe.json',result)
    public = BASE/('PG'+slot.name.removeprefix('pg'));public.mkdir()
    write(public/'manifest.json',{**result,'begin':begin,'privateLogCopiedToGit':False})
    print(json.dumps(dict(actualExit=code,source=source,baselineUnchanged=after==before,
                         publicManifestSha256=sha(public/'manifest.json'),independentQualification='PENDING')))
    require(after == before and snap_after == source_inputs, 'all source inputs and original baseline remain identical')
    raise SystemExit(code)


if __name__ == '__main__':
    main()
