"""Current20 PMD individual decisions: direct-Java premise, native failure/identity/claim contracts."""
from collections import Counter
import copy
import datetime as dt
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile
import pg9134_api_observation_worker_host_v2 as selected
from host_tool_invocation import capture,verify

host=selected.run.host
OUT=host.BASE/'PG9135-api-observation-worker-context-v1'
STATIC=host.BASE/'PG9133-api-observation-worker-static-v2/manifest.json'
STATIC_SHA='9d844d3632a1dda9d9fcad0d36e1303a37786faefe1a786f431efbcedcef2832'
HOST=host.W/'pg9134-api-observation-worker-host-v2/manifest.safe.json'
HOST_SHA='af479ed66e9be54b36e76ef70da64f1180ce4321336deb9f6d8605b0420e1cb6'
MAIN='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/OwnedApiObservationWorker.java'
UNIT='src/deployment/systemd/schubert-nk-api.service.template'
FORMAL='8b91944df5820535e23ba2469740f1c0aa94c447'
SS='documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md'


def context(rows,text,unit,paths):
    starts=[line for line in unit.splitlines() if line.startswith('ExecStart=')]
    assert len(starts)==1 and starts[0].startswith('ExecStart=!/usr/bin/java ') and ' dev.codex.schubert.nk.batch.file.RootServiceLauncher API' in starts[0]
    assert not any(path.endswith(('.war','.ear','/WEB-INF/web.xml','/META-INF/application.xml','/META-INF/ejb-jar.xml')) for path in paths)
    assert Counter(row['rule'] for row in rows)==Counter(DoNotUseThreads=10,AvoidCatchingGenericException=8,AvoidSynchronizedStatement=1,CompareObjectsWithEquals=1)
    assert 'private final Thread worker;' in text and 'Thread.currentThread() == worker' in text
    assert text.index('starting.set(true);')<text.index('starter.accept(worker);')<text.index('startReturned.countDown();')
    assert 'if (firstRemaining <= 0) throw new IOException(UNCONFIRMED);' in text
    assert 'if (!worker.join(Duration.ofNanos(remaining))) throw new IOException(UNCONFIRMED);' in text
    lines=text.splitlines()
    for row in rows:
        assert row['class']=='OwnedApiObservationWorker' and row['package']=='dev.codex.schubert.nk.api.monitoring'
        line=lines[int(row['beginline'])-1];column=int(row['begincolumn'])-1
        if row['rule']=='DoNotUseThreads':assert line[column:].startswith('Thread')
        elif row['rule']=='AvoidCatchingGenericException':assert line[column:].startswith(('RuntimeException','Error')) and 'catch (' in line
        elif row['rule']=='AvoidSynchronizedStatement':assert line[column:].startswith('synchronized (startLock)')
        else:assert 'Thread.currentThread() == worker' in line and row['method']=='awaitStopped'


def main():
    invocation=capture(Path(__file__));assert not OUT.exists() and host.sha(STATIC)==STATIC_SHA and host.sha(HOST)==HOST_SHA
    raw=json.loads(STATIC.read_bytes());actual=json.loads(HOST.read_bytes())
    assert raw['source']==actual['source']==selected.SOURCE and actual['actualExit']==0
    assert len(actual['cases'])==44 and all(row['result']=='PASS' and not row['nonPass'] for row in actual['cases'])
    names=[]
    for file in (HOST.parent/'xml').glob('TEST-*.xml'):
        assert actual['xmlHashes'][file.name]==host.sha(file)
        for case in ET.parse(file).getroot().findall('testcase'):
            assert not list(case);names.append(case.get('name'))
    assert set(names)=={'obsOwn'+str(i).zfill(3) for i in range(1,45)}
    for name in ('checkstyle','spotbugs'):
        row=raw['static'][name];assert row['receipt']['actualExit']==0 and row['receipt']['timedOut'] is False and row['findings']==row['processingErrors']==0
    pmd=raw['static']['pmd'];assert pmd['receipt']['actualExit']==4 and pmd['processingErrors']==0 and pmd['findings']==20
    xml=host.W/'pg9133-api-observation-worker-static-v2/pmd.xml';assert host.sha(xml)==pmd['reportSha256']
    parsed=[dict(node.attrib,message=' '.join(''.join(node.itertext()).split())) for node in ET.parse(xml).getroot().findall('.//{*}violation')]
    canonical=lambda rows:Counter(json.dumps(row,sort_keys=True) for row in rows)
    assert canonical(parsed)==canonical(pmd['rawFindings'])
    normal=json.loads((selected.COMPILE/'manifest.safe.json').read_bytes());assert host.sha(selected.COMPILE/'manifest.safe.json')==selected.COMPILE_SHA
    inputs=normal['begin']['inputHashes'];text=(host.ROOT/MAIN).read_text();unit=(host.ROOT/UNIT).read_text()
    digest=host.sha(host.ROOT/MAIN);assert digest==inputs[MAIN]==raw['sourceHashes'][MAIN] and host.sha(host.ROOT/UNIT)==inputs[UNIT]
    assert all(host.sha(Path(path))==digest for path,digest in raw['toolHashes'].items())
    formal=subprocess.check_output(['git','show',FORMAL+':'+SS],cwd=host.ROOT)
    assert host.sha(host.ROOT/SS)=='3775cb1faf0b96572f4913d06682100da1861f1d364a66f4118b03e27abf4b82' and formal==(host.ROOT/SS).read_bytes()
    api=normal['jars']['api'];assert host.sha(Path(api['path']))==api['sha256'] and api['path'].endswith('.jar')
    with zipfile.ZipFile(api['path']) as archive:members=archive.namelist()
    context(parsed,text,unit,[*inputs,*members])
    vendor=host.TC/'static-gates-20261015/pmd-bin-7.28.0/lib/pmd-java-7.28.0.jar'
    assert host.sha(vendor)==raw['toolHashes'][str(vendor)]=='068b2b5fb276559c32d52e3675d297a458bf27fe181b675cee10555a55c131bd'
    with zipfile.ZipFile(vendor) as archive:rules=ET.fromstring(archive.read('category/java/multithreading.xml'))
    found=[row for row in rules.findall('{*}rule') if row.get('name')=='DoNotUseThreads'];assert len(found)==1
    premise=' '.join(''.join(found[0].find('{*}description').itertext()).split());assert 'J2EE' in premise and 'managed' in premise
    rejected=[]
    wrong=copy.deepcopy(parsed);wrong[0]['rule']='UNKNOWN'
    for name,rows,source,template,paths in (
      ('changed-rule',wrong,text,unit,inputs),
      ('web-container',parsed,text,unit,[*inputs,'unexpected.war']),
      ('non-java-unit',parsed,text,unit.replace('ExecStart=!/usr/bin/java ','ExecStart=/usr/bin/caddy ',1),inputs),
      ('identity-by-value',parsed,text.replace('Thread.currentThread() == worker','Thread.currentThread().equals(worker)',1),unit,inputs),
      ('initial-budget-not-guarded',parsed,text.replace('firstRemaining <= 0','firstRemaining < 0',1),unit,inputs)):
        try:context(rows,source,template,paths)
        except (AssertionError,ValueError):rejected.append(name)
        else:raise AssertionError('context mismatch accepted')
    reasons={
      'DoNotUseThreads':('CONTEXT_NOT_APPLICABLE_J2EE_RULE','Vendor J2EE/container-managed thread premise is false for this API role: current jar/no WAR-EAR/approved standalone direct-Java systemd entry. Current same-source private component PT44 proves start/stop/frame behavior only; actual Main/native deployment is still UNRUN_HOLD. No old PT or blanket rule suppression.'),
      'AvoidCatchingGenericException':('NECESSARY_FAILURE_FRAME_CONTRACT_REVIEWED','Current native Runtime/Error unions preserve primary/secondary fatal and stop UNKNOWN after mandatory state updates, never normal NPE fallback. Interrupted notification secondary is retained. Same-source OBSOWN012-018/023-043 assert identity, compound errors, interruption restoration and no false successful close.'),
      'AvoidSynchronizedStatement':('NECESSARY_PRIVATE_CLAIM_LOCK_REVIEWED','411 private final startLock only claims one invocation. Starter/start drain is outside this monitor and tracked by starting/latch, so stop does not block on SQL/start port. Current 004-009/033-034 prove one start, NEW not falsely stopped and bounded retained start.'),
      'CompareObjectsWithEquals':('EXACT_THREAD_OWNER_IDENTITY_REQUIRED','Self-join prohibition concerns the exact private Thread object, not a value/name-equivalence comparison. OBSOWN035 rejects this worker itself; other callers in current 003-044 wait the captured worker. Neither thread name nor provider equality is an ownership credential.')}
    decisions=[]
    for row in parsed:
        classification,reason=reasons[row['rule']]
        decisions.append(dict(raw=row,classification=classification,reason=reason,sourcePath=MAIN,sourceSha256=digest,sourceOrRulesChanged=False,suppressionAdded=False,
          ordinaryTestWitness='PG9134-api-observation-worker-host-v2:OBSOWN001..044'))
    verify(invocation);OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=selected.SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      currentHostManifestSha256=HOST_SHA,rawStaticManifestSha256=STATIC_SHA,staticDispositions=decisions,rawPmd=20,contextNotApplicableJ2ee=10,
      checkstyle=0,spotbugs=0,unclassified=0,actualViolationsOutstanding=0,unitSha256=inputs[UNIT],formalDesignSource=FORMAL,
      formalDesignSha256=host.sha(host.ROOT/SS),vendorJarSha256=host.sha(vendor),apiJarSha256=api['sha256'],metadataCounterexamples=rejected,
      productTestsExecuted=0,oldSourceResultsTransferred=False,suppressionsAdded=False,actualMainNativePt='UNRUN_HOLD',formalUpdated=False,newAccepted=0))
    print(json.dumps(dict(actualExit=0,reviewedPmd=20,contextNotApplicableJ2ee=10,unclassified=0,spotbugs=0,manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':main()
