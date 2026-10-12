"""Independent corrected-source whole regression qualification; no native/formal claim."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from lan_server import run

W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
CODE = r'''
import datetime,hashlib,json,xml.etree.ElementTree as E,zipfile
from pathlib import Path
B=Path('/home/mini/schubert-nk-pgpt');S=B/'source-full-PG1532';O=B/'runs/PG1532-six-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(v):
 if not v:raise ValueError('corrected whole-source independent qualification refused')
v=json.loads((O/'manifest.safe.json').read_bytes());b=json.loads((O/'begin.safe.json').read_bytes())
require(v['actualExit']==v['mavenExit']==0 and v['issues']==[] and v['sourceInputsUnchanged'] is True)
require(v['productionSource']==b['productionSource']=='4d6bcbddb417b76d27e52d5d9640752c300edccf')
require(v['sourceSnapshotHead']==b['sourceSnapshotHead'] and all(sha(S/p)==h for p,h in b['inputs'].items()))
require(sha(B/'transfer/PG1532-source.tar')==b['sourceArchiveSha256'])
expected={'protocol':(81,17,174),'storage':(163,23,74),'bootstrap':(298,40,105),'api':(963,157,401),'web':(886,129,315),'batch':(1192,158,568)}
require(set(v['modules'])==set(expected))
start=datetime.datetime.fromisoformat(b['startUTC']).timestamp()*1e9;end=datetime.datetime.fromisoformat(v['endUTC']).timestamp()*1e9
old=json.loads((B/'runs/PG1476-six-v1/manifest.safe.json').read_bytes());counts={};changed=[];added=[];coverage={};jars={};inputs={}
for m,(nt,ns,nc) in expected.items():
 t=S/f'src/schubert-nk-{m}/target';a=v['modules'][m];paths=list((t/'surefire-reports').glob('TEST-*.xml'));n=0;identities=set()
 require(len(paths)==ns and (a['tests'],a['suites'],a['mainClasses'])==(nt,ns,nc))
 require(all(a[k]==0 for k in ['failures','errors','skipped','flaky','staticIssues']))
 require(set(a['xmlHashes'])=={p.name for p in paths})
 for p in paths:
  x=E.parse(p).getroot();cs=x.findall('testcase');require(int(x.attrib['tests'])==len(cs) and all(int(x.attrib[k])==0 for k in ['failures','errors','skipped']))
  require(start<=p.stat().st_mtime_ns<=end and sha(p)==a['xmlHashes'][p.name])
  for c in cs:
   key=(c.attrib['classname'],c.attrib['name']);require(key not in identities);identities.add(key)
   require(not any(c.find(k)is not None for k in ['failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError']))
  n+=len(cs)
 require(n==nt)
 spot=t/'spotbugsXml.xml';require(not E.parse(spot).getroot().findall('.//BugInstance'))
 jar=t/f'schubert-nk-{m}-0.1.0-SNAPSHOT.jar'
 with zipfile.ZipFile(jar)as z:classes={p:hashlib.sha256(z.read(p)).hexdigest()for p in z.namelist()if p.endswith('.class')}
 require(classes==a['mainClassHashes'] and len(classes)==nc)
 require(set(classes)=={str(p.relative_to(t/'classes'))for p in(t/'classes').rglob('*.class')})
 require(all(h==sha(t/'classes'/p)for p,h in classes.items()))
 prev=old['modules'][m]['mainClassHashes'];require(set(prev)<=set(classes))
 changed.extend(m+':'+p for p in prev if prev[p]!=classes[p]);added.extend(m+':'+p for p in set(classes)-set(prev))
 tree=E.parse(t/'site/jacoco/jacoco.xml').getroot();counters={c.attrib['type']:{k:int(c.attrib[k])for k in ['missed','covered']}for c in tree.findall('counter')}
 require(counters==a['coverage'] and [dict(x.attrib)for x in tree.findall('sessioninfo')]==a['sessions'] and a['sessions'])
 coverage[m]=counters;counts[m]={'tests':n,'suites':ns,'mainClasses':nc};jars[m]=sha(jar)
 inputs[m]={'coverageXml':sha(t/'site/jacoco/jacoco.xml'),'exec':sha(t/'jacoco.exec'),'static':sha(spot)}
 if m=='storage':
  cs=[c for c in tree.findall('.//class')if c.attrib['name']=='dev/codex/schubert/nk/storage/LinuxFilesystemClassifier'];require(len(cs)==1)
  classifier={c.attrib['type']:{k:int(c.attrib[k])for k in ['missed','covered']}for c in cs[0].findall('counter')}
  require(all(classifier[k]['missed']==0 and classifier[k]['covered']>0 for k in ['LINE','METHOD','CLASS','BRANCH']))
require(set(changed)=={'batch:dev/codex/schubert/nk/batch/file/InspectorEnvironmentReader$NioIo.class','batch:dev/codex/schubert/nk/batch/file/EnvironmentInodePolicy.class'})
require(set(added)=={'storage:dev/codex/schubert/nk/storage/LinuxFilesystemClassifier.class','storage:dev/codex/schubert/nk/storage/LinuxFilesystemClassifier$StatfsCall.class'})
require(v['tests']==sum(x['tests']for x in counts.values())==3583 and sum(x['suites']for x in counts.values())==524 and sum(x['mainClasses']for x in counts.values())==1637)
print(json.dumps({'actualExit':0,'sourceSnapshot':v['sourceSnapshotHead'],'productionSource':v['productionSource'],'tests':3583,'suites':524,'mainClasses':1637,'FESFlakyNotRun':0,'staticSixModules':0,'modules':counts,'changedClasses':sorted(changed),'addedClasses':sorted(added),'jarHashes':jars,'qualificationInputs':inputs,'coverage':coverage,'classifierCoverage':classifier,'classifierFourCounters100':True,'serverManifestSha256':sha(O/'manifest.safe.json'),'sourceArchiveSha256':b['sourceArchiveSha256'],'elapsedSeconds':v['elapsedSeconds'],'startUTC':v['startUTC'],'endUTC':v['endUTC'],'sameSourceNativePending':True,'global100':False,'formalAccepted':False}))
'''

def main():
    os.umask(0o077)
    out = W / 'pg1533-filesystem-full-qualified-v1'
    out.mkdir(mode=0o700)
    root = Path(__file__).resolve().parents[2]
    local = W / 'pg1532-server-six-v1'
    begun = json.loads((local / 'begin.safe.json').read_bytes())
    if subprocess.check_output(['git', 'diff', '4d6bcbddb417b76d27e52d5d9640752c300edccf', begun['snapshot'], '--', 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization'], cwd=root):
        raise ValueError('snapshot differs from corrected qualified source')
    archive_sha = hashlib.sha256((local / 'source.tar').read_bytes()).hexdigest()
    if archive_sha != begun['transferHashes']['/home/mini/schubert-nk-pgpt/transfer/PG1532-source.tar']:
        raise ValueError('host immutable archive provenance differs')
    compile(CODE, '<independent whole source qualification>', 'exec')
    code, status = run("python3 - <<'PG1533'\n" + CODE + '\nPG1533', timeout=90)
    (out / 'observer.private.log').write_text(status)
    value = {'actualExit': code, 'qualificationSourceSha256': hashlib.sha256(CODE.encode()).hexdigest(), 'formalAccepted': False}
    if code == 0:
        value['result'] = json.loads(next(s for s in status.splitlines() if s.strip().startswith('{')))
        if value['result']['sourceSnapshot'] != begun['snapshot'] or value['result']['sourceArchiveSha256'] != archive_sha:
            raise ValueError('server archive/source differs from preserved host transfer')
    with (out / 'manifest.safe.json').open('x') as f:
        json.dump(value, f, sort_keys=True); f.flush(); os.fsync(f.fileno())
    print(json.dumps(value))
    return code

if __name__ == '__main__':
    raise SystemExit(main())
