"""Immutable PG670 selected qualification; never old43/static1 or old native union."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile

T=Path('/home/mini/codex/project1/work/pgpt-foundation');W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
SOURCE='7d658cfe5'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def classes(p):
    with zipfile.ZipFile(p)as z:return {n:z.read(n)for n in z.namelist()if n.endswith('.class')}


def main():
    os.umask(0o077);run=W/'pg670-entry-component-v1';source=(run/'source').read_text().strip()
    assert source.startswith(SOURCE)and(run/'exit').read_bytes()==b'0\n'
    entries=[l.split('  ',1)for l in(run/'source-files.sha256').read_text().splitlines()]
    for expected,path in entries:
        assert hashlib.sha256(subprocess.check_output(['git','show',source+':'+path],cwd=T)).hexdigest()==expected
    begin=datetime.datetime.fromisoformat((run/'started').read_text().strip()).timestamp();end=datetime.datetime.fromisoformat((run/'completed').read_text().strip()).timestamp()
    expected={'dev.codex.schubert.nk.api.bootstrap.BootstrapEntryBoundaryTest':5,'dev.codex.schubert.nk.api.bootstrap.BootstrapAdminMainTest':4,
              'dev.codex.schubert.nk.api.maintenance.InspectorEntryBoundaryTest':4,'dev.codex.schubert.nk.api.maintenance.InspectorLauncherTest':8,
              'dev.codex.schubert.nk.api.file.InspectorApplicationTest':9,'dev.codex.schubert.nk.api.maintenance.InspectorProcessTest':14}
    paths=sorted((run/'surefire-reports').glob('TEST-*.xml'));assert{p.name for p in paths}=={'TEST-'+n+'.xml'for n in expected}
    for p in paths:
        xml=ET.parse(p).getroot();name=xml.get('name');assert xml.get('tests')==str(expected[name])and all(xml.get(k)=='0'for k in('failures','errors','skipped'))
        cases=xml.findall('testcase');assert len(cases)==expected[name]and len({c.get('name')for c in cases})==len(cases)
        assert all(not c.findall(k)for c in cases for k in('failure','error','skipped','flakyFailure','rerunFailure','rerunError'))
        assert begin-1<=p.stat().st_mtime<=end+2
    root=ET.parse(run/'jacoco.xml').getroot();sessions=root.findall('sessioninfo');assert len(sessions)==1
    for s in sessions:assert begin*1000-1000<=int(s.get('start'))<=int(s.get('dump'))<=end*1000+1000
    bugs=ET.parse(run/'spotbugsXml.xml').getroot();assert not bugs.findall('BugInstance')and not bugs.findall('.//Error')
    helper={}
    for cls,method in(('dev/codex/schubert/nk/api/bootstrap/BootstrapAdminMain','launch'),('dev/codex/schubert/nk/api/maintenance/InspectorLauncher','complete')):
        nodes=[m for c in root.findall('.//class')if c.get('name')==cls for m in c.findall('method')if m.get('name')==method];assert len(nodes)==1
        counters={c.get('type'):{'missed':int(c.get('missed')),'covered':int(c.get('covered'))}for c in nodes[0].findall('counter')}
        assert all(counters[k]['missed']==0 and counters[k]['covered']>0 for k in('LINE','METHOD','BRANCH'));helper[method]=counters
    old=W/'pg630-retention-factory-six-host-v1/api/schubert-nk-api-0.1.0-SNAPSHOT.jar';new=run/'schubert-nk-api-0.1.0-SNAPSHOT.jar';a=classes(old);b=classes(new)
    added=sorted(set(b)-set(a));changed=sorted(n for n in a.keys()&b.keys()if a[n]!=b[n]);assert not a.keys()-b.keys()
    assert added==sorted(['dev/codex/schubert/nk/api/bootstrap/BootstrapAdminMain$Capture.class','dev/codex/schubert/nk/api/bootstrap/BootstrapAdminMain$Operation.class','dev/codex/schubert/nk/api/maintenance/InspectorLauncher$Capture.class'])
    assert changed==sorted(['dev/codex/schubert/nk/api/bootstrap/BootstrapAdminMain.class','dev/codex/schubert/nk/api/maintenance/InspectorLauncher.class'])
    log=(run/'build.private.log').read_text();assert log.count('BUILD SUCCESS')==1 and 'BUILD FAILURE'not in log and 'qualifiedNullableFixtures'in log
    record={'run':'PG670-entry-component-v1','actualExit':0,'candidateSource':source,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip(),
            'timeUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'selectedTests':44,'suites':6,'newEntryCases':9,'FESflakyRerun':0,'staticApiIssues':0,'nullAwayCompilePassed':True,
            'elapsedSeconds':end-begin,'jarSha256':sha(new),'execSha256':sha(run/'api.exec'),'helperCounters':helper,'changedMainClasses':changed,'addedAbstractInterfaces':added,
            'coverageSessions':[{'idSha256':hashlib.sha256(s.get('id').encode()).hexdigest(),'start':int(s.get('start')),'dump':int(s.get('dump'))}for s in sessions],
            'sourceSnapshotSha256':sha(run/'source-files.sha256'),'hashes':{p.name:sha(p)for p in[run/'jacoco.xml',run/'spotbugsXml.xml',*paths]},'deployedSource':'36fe7a0b938489d61d17d49c1c30a6fbbef699d5',
            'oldNativeNotImported':True,'globalCoverage100':False,'wholeRegressionNotRun':True,'formalAccepted':False,'rawExported':False}
    with(run/'manifest.safe.json').open('x')as f:json.dump(record,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'selectedTests':44,'suites':6,'staticApi0':True,'helpersLineMethodBranch100':True,'classDelta':'2 changed/3 abstract added','manifestSha256':sha(run/'manifest.safe.json'),'formalAccepted':False}))


if __name__=='__main__':main()
