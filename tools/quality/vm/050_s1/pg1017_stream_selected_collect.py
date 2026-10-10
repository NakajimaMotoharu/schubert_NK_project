"""Fresh selected XML/counter/static/byte qualifier, independent fixed expected outcomes."""
import datetime
import json
import os
import subprocess
import xml.etree.ElementTree as E
from pathlib import Path
from pg831_manager_collect import sha, classes
from pg1013_qualified_dependency_cache import dependency_bytes

T=Path(__file__).resolve().parents[4]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')

def main():
    os.umask(0o077)
    p=W/'pg1016-stream-selected-v7';a=json.loads((p/'run.safe.json').read_bytes())
    assert a['actualExit']==0 and a['source']=='2db946551bc8ed861acd277af3c31285d633d097'
    begin=datetime.datetime.fromisoformat(a['startedUTC']).timestamp()
    end=datetime.datetime.fromisoformat(a['endedUTC']).timestamp()
    expected={'InspectorUnitProbeTest':11,'BrokerJournalQueryTest':5,'InspectorHeldStateContractTest':9,'InspectorUnitSnapshotTest':9}
    paths=list((p/'batch').glob('TEST-*.xml'));assert len(paths)==4
    sums={k:0 for k in ('tests','failures','errors','skipped')};hashes={};names=set()
    for f in paths:
        root=E.parse(f).getroot();suite=root.get('name').rpartition('.')[2]
        assert int(root.get('tests'))==expected[suite]
        cases=root.findall('testcase');assert len(cases)==expected[suite]
        assert not any(x.tag.lower() in ('failure','error','skipped','flakyfailure','flakyerror','rerunfailure','rerunerror')for x in root.iter())
        original=T/'src/schubert-nk-batch/target/surefire-reports'/f.name
        assert sha(original)==sha(f) and begin<=original.stat().st_mtime<=end+1
        for k in sums:sums[k]+=int(root.get(k,'0'))
        hashes[f.name]=sha(f);names.update(c.get('name')for c in cases)
    assert sums=={'tests':34,'failures':0,'errors':0,'skipped':0}
    assert {'streamingStartIoFailureIsSanitizedWithoutRetry','streamingLiteralByteLimitAndOverflowCloseActualProcess','streamingReadFaultPreservesUnknownFailureAndSanitizesIo'}<=names
    bugs=E.parse(p/'batch/spotbugsXml.xml').getroot()
    assert not bugs.findall('.//BugInstance') and not bugs.findall('.//Error')
    coverage=E.parse(p/'batch/jacoco.xml').getroot()
    target=next(c for c in coverage.findall('.//class')if c.get('name')=='dev/codex/schubert/nk/batch/platform/InspectorUnitProbe$NativeReader')
    counters={c.get('type'):{'covered':int(c.get('covered')),'missed':int(c.get('missed'))}for c in target.findall('counter')}
    for k,n in {'METHOD':20,'CLASS':1,'BRANCH':24}.items():assert counters[k]=={'covered':n,'missed':0}
    assert counters['LINE']=={'covered':128,'missed':1}
    jar='schubert-nk-batch-0.1.0-SNAPSHOT.jar'
    old=W/'pg926-body-six-host-v1'
    assert sha(old/'manifest.safe.json')=='4ae512d3b3a8e85d81fcd8e9ef04279fff58114c42e9b158adc61299d8211fdf'
    assert classes(p/'batch'/jar)==classes(old/'batch'/jar)
    record={'actualExit':0,'run':p.name,'source':a['source'],'productionMainSource':'40ef6e894573d2ffab1d1732124960f9c98d5f97',
      'tests':34,'suites':4,'FESFlakyNotRunIndicators':0,'staticIssues':0,'nativeReaderCounters':counters,
      'dependencyClassCounts':dependency_bytes(),'all343BatchMainBytesEqualQualified926':True,
      'testIds':['PT-DEP-1007001','PT-DEP-1007002','PT-DEP-1015001'],'xmlHashes':hashes,
      'runManifestSha256':sha(p/'run.safe.json'),'coverageSha256':sha(p/'batch/jacoco.xml'),
      'staticSha256':sha(p/'batch/spotbugsXml.xml'),'elapsedSeconds':end-begin,
      'collectorHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip(),
      'nativeReaderFourCounter100':False,'unaccepted':['NativeReader caller line212 remains missed despite actual provider failures; do not exclude or claim100'],
      'wholeRegressionPending':True,'formalAccepted':False,'wholeWbsAccepted':False,'rawExported':False}
    with(p/'qualified.safe.json').open('x')as f:json.dump(record,f,sort_keys=True)
    print(json.dumps({k:v for k,v in record.items()if k!='xmlHashes'}))

if __name__=='__main__':main()
