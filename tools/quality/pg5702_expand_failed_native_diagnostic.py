"""Expand existing failedRoot diagnostic only; no VM read, new capture, PT run or success claim."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg5700_failed_native_diagnostic import ROOT,W,MODULES

SLOT='pg5702-expanded-failed-native-v1'


def main():
    original=W/'pg5700-failed-native-diagnostic-v2';before=json.loads((original/'manifest.safe.json').read_bytes())
    p=original/'failed-parent.private.exec'
    if not(before['actualExit']==0 and before['rootExit']==30 and before['diagnosticOnly']is True and before['normalNativeQualified']is False
      and before['classByteMismatch']==0 and hashlib.sha256(p.read_bytes()).hexdigest()==before['nativeSha256']):raise ValueError('original failed native unchanged, not a normal source qualification')
    whole=json.loads((ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5588-current3905-cases/qualification.json').read_bytes())
    roots=[W/'pg5566-private-monitor-green-v3/source'/('src/schubert-nk-'+m+'/target/classes')for m in MODULES]
    actual={m+':'+f.relative_to(r).as_posix():hashlib.sha256(f.read_bytes()).hexdigest()for m,r in zip(MODULES,roots)for f in r.rglob('*.class')}
    if actual!=whole['allPhysicalMainSha256']or len(actual)!=1664:raise ValueError('every same actual class, no baseline result transfer')
    libs=[Path(n)for n in before['libraryHashes']]
    if any(hashlib.sha256(f.read_bytes()).hexdigest()!=before['libraryHashes'][str(f)]for f in libs):raise ValueError('original validated library bytes')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);classes=out/'classes';classes.mkdir();cp=os.pathsep.join(map(str,libs));jdk=ROOT.parent/'toolchain/jdk-25.0.4/bin'
    env={k:v for k,v in os.environ.items()if k not in('JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','CLASSPATH')}
    commands=[[str(jdk/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(classes),str(ROOT/'tools/quality/FailedRootCoverageDiagnostic.java')],
      [str(jdk/'java'),'-Xmx512m','-cp',str(classes)+os.pathsep+cp,'FailedRootCoverageDiagnostic',str(p),*map(str,roots),'ALL_SOURCE']]
    for i,command in enumerate(commands):
        with(out/('phase-'+str(i)+'.private.log')).open('xb')as f:r=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,env=env,timeout=90)
        if r.returncode:raise ValueError('original failed native/class analysis refused')
    targets=[]
    for line in(out/'phase-1.private.log').read_text().splitlines():
        a=line.split('\t')
        if a[0]!='LINE'or int(a[3])==0 or int(a[4])!=0:continue
        parts=a[1].split('/');module=parts[4]if len(parts)>4 else''
        file=ROOT/('src/schubert-nk-'+module+'/src/main/java')/(a[1].split('$')[0]+'.java')
        if not file.exists():continue
        lines=file.read_text().splitlines();source=lines[int(a[2])-1].strip()
        if 'throw 'in source:targets.append({'class':a[1],'line':int(a[2]),'source':source,'coveredInstructions':int(a[3]),'missedInstructions':int(a[4])})
    value={'actualExit':0,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':before['source'],'rootExit':30,
      'originalFailedNativeSha256':before['nativeSha256'],'classMainCount':1664,'classByteMismatch':0,'coveredThrowLineCandidates':targets,
      'vmOperations':0,'newCapture':False,'wholeMorningAccepted':False,'normalNativeQualified':False,'formalAccepted':False,
      'helperSha256':hashlib.sha256((ROOT/'tools/quality/FailedRootCoverageDiagnostic.java').read_bytes()).hexdigest()}
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'rootExit':30,'candidates':targets,'normalNativeQualified':False}))


if __name__=='__main__':main()
