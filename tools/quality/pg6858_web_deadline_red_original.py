"""Read original failed own-component counterexamples; never relabel failure or not-run as PASS."""
import hashlib
import json
import os
import subprocess
import tarfile
from pathlib import PurePosixPath
import xml.etree.ElementTree as ET
import pg6850_web_deadline_selected as selected
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg5966_api_sql_selected import source_test_names

FULL=BASE/'PG6828-current4203-cases/qualification.json'
FULLSHA='87d3de1b887514b10838d3cef748e9421f17574c87ae89a37f5b616a8e1f4dc0'
SOURCE='63559b277200578e5b60c74181e198817f34c336'
NAMES={
 'webMgmt335001ZeroBudgetDoesNotWaitForOtherCloseOwner':'PT-WEB-MGMT335001',
 'webMgmt335002InterruptDuringLockReturnsUnknownWithNotification':'PT-WEB-MGMT335002',
 'webMgmt335003PreInterruptDuringStartContentionRefusesLatePromotion':'PT-WEB-MGMT335003'}
CLASS='dev.codex.schubert.nk.web.bootstrap.WebManagementDeadlineTest'


def main():
    run=W/'pg6856-web-deadline-red-v3';mp=run/'manifest.safe.json';bp=run/'begin.safe.json'
    m,b=[json.loads(p.read_bytes())for p in(mp,bp)]
    if not(m['source']==b['source']==SOURCE and m['actualExit']==m['mavenActualExit']==1
      and m['phaseExits']==[0,0,1]and m['sourceFixed']and(m['tests'],m['suites'])==(13,6)
      and not m['selectedQualified']and not m['exactInventory']):raise ValueError('original red terminal, no whole/green claim')
    if sha(FULL)!=FULLSHA or sha(run/'source.tar')!=m['archiveSha256']or m['archiveSha256']!=b['archiveSha256']:raise ValueError('frozen full identity/source archive')
    selected.red_guard(SOURCE)
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('original Main/Test/gates remain fixed')
    inputs={};snapshot=run/'source'
    with tarfile.open(run/'source.tar')as archive:
        for item in archive:
            if item.isdir():continue
            path=PurePosixPath(item.name)
            if not item.isfile()or path.is_absolute()or'..'in path.parts or item.name in inputs:raise ValueError('unique regular archived inputs')
            value=hashlib.sha256(archive.extractfile(item).read()).hexdigest()
            if sha(snapshot/item.name)!=value:raise ValueError('each original input remains archived byte')
            inputs[item.name]=value
    old=json.loads(FULL.read_bytes());main={p.relative_to(snapshot).as_posix():sha(p)for p in snapshot.glob('src/*/src/main/java/**/*.java')}
    if len(main)!=851 or main!=old['allSourceHashes']or m['allPhysicalMainSha256']!=old['allPhysicalMainSha256']:raise ValueError('all851/1669 prior Main exact, no artificial input state')
    cases,_=selected.inventory(True);expected=set()
    for module,names in cases.items():
        for name in names:
            cls='dev.codex.schubert.nk.'+name
            path=snapshot/('src/schubert-nk-'+module+'/src/test/java')/(cls.replace('.','/')+'.java')
            expected.update((cls,n)for n in source_test_names(path))
    if len(expected)!=15:raise ValueError('explicit original15 declarations')
    text=(snapshot/selected.TEST).read_text();sites=[i+1 for i,s in enumerate(text.splitlines())if 'Outcome actual = second.get('in s]
    if len(sites)!=1 or sha(snapshot/selected.TEST)!=sha(ROOT/selected.TEST):raise ValueError('same fixed counterexample Test and one second-get site')
    observed=set();failures=[];xmls={}
    for module in('protocol','storage','bootstrap','api','web','batch'):
        for p in(snapshot/('src/schubert-nk-'+module+'/target/surefire-reports')).glob('TEST-*.xml'):
            tree=ET.parse(p).getroot();cls=tree.get('name')
            if cls in xmls or sha(p)!=m['xmlHashes'][cls]['sha256']:raise ValueError('each original unique XML hash')
            xmls[cls]=sha(p)
            if int(tree.get('tests'))!=len(tree.findall('testcase')):raise ValueError('actual XML declaration count')
            for case in tree.findall('testcase'):
                name=case.get('name').split('(',1)[0];key=(cls,name)
                if key not in expected or key in observed:raise ValueError('only exact original case identities')
                observed.add(key)
                faults=[x for x in case.iter()if x.tag in('failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError')]
                if not faults:continue
                if cls!=CLASS or name not in NAMES or len(faults)!=1:raise ValueError('no unrelated fault/skip/flaky accepted')
                fault=faults[0];frame=f'{CLASS}.exercise(WebManagementDeadlineTest.java:{sites[0]})'
                if fault.tag!='error'or fault.get('type')!='java.util.concurrent.TimeoutException'or frame not in(fault.text or ''):raise ValueError('original second-get timeout, never cleanup failure as reproduction')
                failures.append(dict(testId=NAMES[name],method=name,originalXmlSha256=sha(p),originalFailureType=fault.get('type'),fixtureFrameLine=sites[0],
                  originalFailureRetained=True,cleanupScope='Java pending timeout survives only after all nested finally assertions/rebind return normally; own fixture only, not live Web/Root'))
    missing=expected-observed
    if len(observed)!=13 or len(xmls)!=6 or len(failures)!=3 or{r['method']for r in failures}!=set(NAMES)or len(missing)!=2:raise ValueError('exact failed3/executed13/not-run2, no PASS arithmetic')
    if{tuple(x)for x in m['failedOrSkipped']}!={(CLASS,n)for n in NAMES}:raise ValueError('genuine failed-case index')
    value=dict(readerActualExit=0,originalActualExit=1,source=SOURCE,originalManifestSha256=sha(mp),sourceArchiveSha256=m['archiveSha256'],
      testSourceSha256=sha(snapshot/selected.TEST),allArchivedInputsExact=True,archivedInputs=len(inputs),all851MainByteExact=True,all1669CompiledMainByteExact=True,
      priorFullIdentitySha256=FULLSHA,originalExpectedTests=15,originalExpectedSuites=8,executedTests=13,executedSuites=6,
      failedTests=3,notRunTests=2,notRunCases=[dict(className=c,method=n)for c,n in sorted(missing)],failures=failures,xmlHashes=xmls,
      sameOracleRequiredForGreen=True,productionCounterexamplesReproduced=3,wholeQualified=False,selectedQualified=False,
      staticObservedOnly=m['staticIssues'],sourceFixed=True,testsExecutedByReader=0,additionalBuildsIssued=0,vmActions=0,
      nativeQualified=False,formalAccepted=False,acceptedLeafDelta=0,effortPercent=None,ptAlternativeCompleted=0,
      toolSha256=sha(ROOT/'tools/quality/pg6858_web_deadline_red_original.py'))
    out=BASE/'PG6858-web-deadline-red-original-v1';os.umask(0o077);out.mkdir();p=out/'manifest.json'
    with p.open('x')as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(readerActualExit=0,originalActualExit=1,counterexamples=3,tests=13,notRun=2,manifestSha256=sha(p))))


if __name__=='__main__':main()
