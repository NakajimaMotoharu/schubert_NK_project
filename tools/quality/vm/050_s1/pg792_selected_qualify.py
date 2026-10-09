"""Independent readonly qualification of actual fixed791 source; no repeated Maven."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from pg791_completion_selected import TESTS,xml_join

T=Path(__file__).resolve().parents[4]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def invoke_then_check(action,check):
    try:action()
    except SystemExit as result:
        if result.code not in (None,0):raise
    return check()


def main():
    os.umask(0o077);run=W/'pg791-completion-selected-v1';record=json.loads((run/'run.safe.json').read_bytes())
    assert record['actualExit']==0 and (run/'exit').read_bytes()==b'0\n'
    assert record['source']=='c035e90ee759fffcfdf070e0a069e977b61d0b54'
    assert not subprocess.check_output(['git','diff','--name-only',record['source'],'--','src','pom.xml'],cwd=T)
    assert all(hashlib.sha256((T/name).read_bytes()).hexdigest()==sha for name,sha in record['sourceHashes'].items())
    assert all(hashlib.sha256((run/name).read_bytes()).hexdigest()==sha for name,sha in record['files'].items())
    joined,count=xml_join(TESTS['batch'],list((run/'batch').glob('TEST-*.xml')));assert joined
    xml=ET.parse(run/'batch/spotbugsXml.xml').getroot();assert not xml.findall('BugInstance')and xml.find('FindBugsSummary').get('total_bugs')=='0'
    coverage=ET.parse(run/'batch/jacoco.xml').getroot();new={}
    for cls in coverage.findall('./package/class'):
        if cls.get('name','').split('/')[-1]in ('MorningStartupLaunchOwner$CompletionPhase','MorningStartupLaunchOwner$CompletionProgress'):
            counters={n.get('type'):{'missed':int(n.get('missed')),'covered':int(n.get('covered'))}for n in cls.findall('counter')}
            assert all(counters[k]['missed']==0 for k in ('LINE','METHOD','CLASS','BRANCH'))
            new[cls.get('name')]=counters
    assert len(new)==2
    value={'actualExit':0,'source':record['source'],'selectedRecordSha256':hashlib.sha256((run/'run.safe.json').read_bytes()).hexdigest(),'selectedSuites':len(TESTS['batch']),'tests':count,'failed':0,'errors':0,'skipped':0,'notRun':0,'staticBugs':0,'newClassCounters':new,'jarSha256':record['files']['batch/schubert-nk-batch-0.1.0-SNAPSHOT.jar'],'qualifierOperatorSource':subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip(),'formalAccepted':False,'noMavenRepeat':True}
    with(W/'pg792-selected-qualification-v1.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps(value))


if __name__=='__main__':main()
