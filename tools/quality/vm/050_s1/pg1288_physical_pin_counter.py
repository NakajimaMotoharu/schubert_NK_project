"""Same-class component diagnostic only; no application native/formal acceptance."""
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from pg1280_held_channel_full_collect import SOURCE,W,sha,require
from pg1257_fresh_independent_terminal_post import SSH
from pg1271_current_native_gap import J,R,COUNTERS


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean operator required')
    require(not subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml']))
    actual=json.loads((W/'pg1286-physical-pin-v1.safe.json').read_bytes())
    post=json.loads((W/'pg1287-current-readonly-v1.safe.json').read_bytes())
    require(actual['actualExit']==post['actualExit']==0 and actual['candidateSource']==SOURCE and actual['componentOnly']is True and not actual['applicationRootUnitStartupAccepted'])
    host=W/'pg1279-held-channel-six-host-v1';qualified=json.loads((host/'manifest.safe.json').read_bytes())
    require(qualified['actualExit']==0 and qualified['candidateSource']==SOURCE)
    target=W/'pg1288-physical-pin-counter-v1';require(not os.path.lexists(target));target.mkdir(mode=0o700)
    data=[host/'bootstrap/jacoco.exec'];require(sha(data[0])==qualified['moduleResults']['bootstrap']['execSha256'])
    for mode in ['RW','RO']:
        expected=actual['phases'][mode];name=mode.lower()+'.exec'
        code="import pathlib,os,stat,hashlib,sys;p=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1286-physical-pin-v1/"+name+"');s=p.lstat();assert stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1);raw=p.read_bytes();assert len(raw)=="+str(expected['execBytes'])+"and hashlib.sha256(raw).hexdigest()=="+repr(expected['execSha256'])+";sys.stdout.buffer.write(raw)"
        result=subprocess.run(SSH,input=code.encode(),capture_output=True,timeout=20)
        require(result.returncode==0 and not result.stderr)
        p=target/name
        with p.open('xb')as f:f.write(result.stdout);f.flush();os.fsync(f.fileno())
        require(sha(p)==expected['execSha256']);data.append(p)
    cp=[];repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    for pattern in ['org/jacoco/org.jacoco.core/0.8.15/*.jar','org/jacoco/org.jacoco.report/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar']:
        paths=list(repo.glob(pattern));require(len(paths)==1);cp.append(str(paths[0]))
    classes=target/'classes';classes.mkdir(mode=0o700)
    result=subprocess.run([str(J/'javac'),'-Xlint:all','-Werror','-cp',':'.join(cp),'-d',str(classes),str(R/'NativeCoverageXml471.java')],capture_output=True,timeout=30)
    require(result.returncode==0 and not result.stdout and not result.stderr);cp.insert(0,str(classes))
    jar=host/'bootstrap/schubert-nk-bootstrap-0.1.0-SNAPSHOT.jar';require(sha(jar)==qualified['moduleResults']['bootstrap']['jarSha256'])
    xml=target/'bootstrap.xml'
    result=subprocess.run([str(J/'java'),'-cp',':'.join(cp),'NativeCoverageXml471',str(jar),str(xml),*[str(p)for p in data]],capture_output=True,timeout=45)
    with(target/'report.private.log').open('xb')as f:f.write(result.stdout+result.stderr);f.flush();os.fsync(f.fileno())
    require(result.returncode==0 and not result.stderr and b'classMismatch0=true'in result.stdout)
    root=ET.parse(xml).getroot();actual_counters={c.attrib['type']:{'missed':int(c.attrib['missed']),'covered':int(c.attrib['covered'])}for c in root.findall('counter')}
    expected_counters=qualified['moduleResults']['bootstrap']['hostCounters']
    require(all(sum(actual_counters[k].values())==sum(expected_counters[k].values())and actual_counters[k]['missed']<=expected_counters[k]['missed']for k in COUNTERS))
    cls=next(c for c in root.findall('package/class')if c.attrib['name'].endswith('/NativeCoveragePrivateFile'))
    private_counters={c.attrib['type']:{'missed':int(c.attrib['missed']),'covered':int(c.attrib['covered'])}for c in cls.findall('counter')}
    safe={'actualExit':0,'candidateSource':SOURCE,'componentActualManifestSha256':sha(W/'pg1286-physical-pin-v1.safe.json'),'independentCurrentPostSha256':sha(W/'pg1287-current-readonly-v1.safe.json'),'frozenHostManifestSha256':sha(host/'manifest.safe.json'),'sameByteNoMatch0':True,'execCount':3,'hostExecCount':1,'componentExecCount':2,'applicationNativeImports0':True,'oldSourceExecImports0':True,'mixedRunsDiagnosticOnly':True,'coverageXmlSha256':sha(xml),'moduleCounters':actual_counters,'privateClassCounters':private_counters,'lineGain':expected_counters['LINE']['missed']-actual_counters['LINE']['missed'],'methodGain':expected_counters['METHOD']['missed']-actual_counters['METHOD']['missed'],'branchGain':expected_counters['BRANCH']['missed']-actual_counters['BRANCH']['missed'],'remainingPrivateMethods':[m.attrib for m in cls.findall('method')if any(int(c.attrib['missed'])for c in m.findall('counter')if c.attrib['type']in COUNTERS)],'formalAccepted':False,'applicationRootUnitStartupAccepted':False}
    with(target/'manifest.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(safe));return 0


if __name__=='__main__':raise SystemExit(main())
