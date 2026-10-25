"""Two actual standalone-API J2EE-premise rows; not an actual Main execution/PT exemption."""
from collections import Counter
import copy
import datetime as dt
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile
import pg9198_api_main_observation_host as selected
from host_tool_invocation import capture, verify

host=selected.run.host
OUT=host.BASE/'PG9199-api-main-observation-review-v1'
RAW=host.BASE/'PG9197-api-main-observation-static-v1/manifest.json'
RAW_SHA='aeddd461450c49be5bcfe78b84cb4bad9bd8b6442fbf8fdda56a211c46e5924e'
HOST=host.W/'pg9198-api-main-observation-host-v1/manifest.safe.json'
HOST_SHA='21a71fdc21ec122913e64689206209fa0a57c61c77258fd39268d4f44c830adb'
MAIN='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiProcessMain.java'
UNIT='src/deployment/systemd/schubert-nk-api.service.template'
FORMAL='8b91944df5820535e23ba2469740f1c0aa94c447'
SS='documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md'

def contract(rows,text,unit,paths):
    starts=[line for line in unit.splitlines() if line.startswith('ExecStart=')]
    assert len(starts)==1 and starts[0].startswith('ExecStart=!/usr/bin/java ')
    assert ' dev.codex.schubert.nk.batch.file.RootServiceLauncher API' in starts[0]
    assert not any(path.endswith(('.war','.ear','/WEB-INF/web.xml','/META-INF/application.xml','/META-INF/ejb-jar.xml')) for path in paths)
    assert Counter(row['rule'] for row in rows)==Counter(DoNotUseThreads=2)
    assert {row['method'] for row in rows}=={'main','fatal'}
    assert 'Thread.currentThread().setUncaughtExceptionHandler(ApiProcessMain::fatal);' in text
    assert 'static void fatal(Thread thread, Throwable failure)' in text
    lines=text.splitlines()
    for row in rows:
        assert row['class']=='ApiProcessMain' and row['package']=='dev.codex.schubert.nk.api.bootstrap'
        assert lines[int(row['beginline'])-1][int(row['begincolumn'])-1:].startswith('Thread')

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    assert host.sha(RAW)==RAW_SHA and host.sha(HOST)==HOST_SHA
    raw=json.loads(RAW.read_bytes()); actual=json.loads(HOST.read_bytes())
    assert raw['source']==actual['source']==selected.SOURCE and raw['actualExit']==1 and actual['actualExit']==0
    assert len(actual['cases'])==8 and all(row['result']=='PASS' and not row['nonPass'] for row in actual['cases'])
    assert {row['name'] for row in actual['cases']}=={'apiObsBoot'+str(i).zfill(3) for i in range(1,9)}
    for role in ('pmd','checkstyle','spotbugs'):
        row=raw['static'][role]
        assert row['receipt']['timedOut'] is False and row['processingErrors']==0
        if role=='pmd': assert row['receipt']['actualExit']==4 and row['findings']==2
        else: assert row['receipt']['actualExit']==0 and row['findings']==0
    pmd=raw['static']['pmd']; xml=host.W/'pg9197-api-main-observation-static-v1/pmd.xml'
    assert host.sha(xml)==pmd['reportSha256']
    parsed=[dict(row.attrib,message=' '.join(''.join(row.itertext()).split())) for row in ET.parse(xml).getroot().findall('.//{*}violation')]
    canonical=lambda rows:Counter(json.dumps(row,sort_keys=True) for row in rows)
    assert canonical(parsed)==canonical(pmd['rawFindings'])
    normal=json.loads((selected.COMPILE/'manifest.safe.json').read_bytes())
    assert host.sha(selected.COMPILE/'manifest.safe.json')==selected.COMPILE_SHA
    hashes=normal['begin']['inputHashes']; text=(host.ROOT/MAIN).read_text(); unit=(host.ROOT/UNIT).read_text()
    assert host.sha(host.ROOT/MAIN)==hashes[MAIN]==raw['sourceHashes'][MAIN] and host.sha(host.ROOT/UNIT)==hashes[UNIT]
    assert all(host.sha(Path(path))==digest for path,digest in raw['toolHashes'].items())
    assert subprocess.check_output(['git','show',FORMAL+':'+SS],cwd=host.ROOT)==(host.ROOT/SS).read_bytes()
    vendor=host.TC/'static-gates-20261015/pmd-bin-7.28.0/lib/pmd-java-7.28.0.jar'
    assert host.sha(vendor)==raw['toolHashes'][str(vendor)]=='068b2b5fb276559c32d52e3675d297a458bf27fe181b675cee10555a55c131bd'
    with zipfile.ZipFile(vendor) as archive: root=ET.fromstring(archive.read('category/java/multithreading.xml'))
    rules=[row for row in root.findall('{*}rule') if row.get('name')=='DoNotUseThreads']; assert len(rules)==1
    premise=' '.join(''.join(rules[0].find('{*}description').itertext()).split())
    assert 'J2EE' in premise and 'managed' in premise
    api=normal['jars']['api']; assert host.sha(Path(api['path']))==api['sha256'] and api['path'].endswith('.jar')
    with zipfile.ZipFile(api['path']) as archive: members=archive.namelist()
    contract(parsed,text,unit,[*hashes,*members]); rejected=[]
    changed=copy.deepcopy(parsed); changed[0]['rule']='UNKNOWN'
    for name,rows,body,template,paths in (
      ('unknown-rule',changed,text,unit,hashes),
      ('container-premise',parsed,text,unit,[*hashes,'unexpected.war']),
      ('wrong-exec-role',parsed,text,unit.replace('ExecStart=!/usr/bin/java ','ExecStart=/usr/bin/caddy ',1),hashes),
      ('changed-subject',parsed,text.replace('Thread.currentThread().setUncaughtExceptionHandler','Thread.ofPlatform().setUncaughtExceptionHandler',1),unit,hashes)):
        try: contract(rows,body,template,paths)
        except (AssertionError,ValueError): rejected.append(name)
        else: raise AssertionError('incorrect applicability accepted')
    decisions=[dict(raw=row,classification='CONTEXT_NOT_APPLICABLE_J2EE_RULE',
      reason='Pinned vendor rule assumes J2EE/container-managed threading. Current source role is approved standalone direct-Java API jar, no WAR/EAR/container descriptors. Current ordinary8 test only factory/release helpers and neither constructs nor runs Main. Applicability review is not native/hook/whole-Main PT or measured coverage.',
      sourcePath=MAIN,sourceSha256=hashes[MAIN],sourceOrRulesChanged=False,suppressionAdded=False,
      currentDynamicMainPt='UNRUN_HOLD',ordinaryFactoryWitness='PG9198-api-main-observation-host-v1:APIOBSBOOT001..008') for row in parsed]
    verify(invocation); OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=selected.SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
      invocation=invocation,currentHostManifestSha256=HOST_SHA,rawStaticManifestSha256=RAW_SHA,
      staticDispositions=decisions,rawPmd=2,contextNotApplicableJ2ee=2,unclassified=0,actualViolationsOutstanding=0,
      rawStaticExit=1,checkstyle=0,spotbugs=0,unitSha256=hashes[UNIT],formalDesignSource=FORMAL,
      formalDesignSha256=host.sha(host.ROOT/SS),vendorJarSha256=host.sha(vendor),apiJarSha256=api['sha256'],
      metadataCounterexamples=rejected,productTestsExecuted=0,oldSourceResultsTransferred=False,
      suppressionsAdded=False,ptExecutionExempt=False,actualMainNativePt='UNRUN_HOLD',qualityGatePass=False,
      programPtComplete=False,whole451Accepted=False,formalUpdated=False,newAccepted=0))
    print(json.dumps(dict(actualExit=0,reviewedPmd=2,unclassified=0,programPtComplete=False,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
