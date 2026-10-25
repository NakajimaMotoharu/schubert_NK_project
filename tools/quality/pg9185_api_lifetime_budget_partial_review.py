"""Current20 PMD individual decisions: direct-Java premise, native failure/identity/claim contracts."""
from collections import Counter
import datetime as dt
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile
import pg9184_api_lifetime_budget_host as selected
from host_tool_invocation import capture,verify

host=selected.run.host
OUT=host.BASE/'PG9185-api-lifetime-budget-partial-review-v1'
STATIC=host.BASE/'PG9183-api-lifetime-budget-static-v1/manifest.json'
STATIC_SHA='9da454967ec0eb9f036dab2b05f73ff29399eb211ee4652b5bbb1a29eb6f6c8f'
HOST=host.W/'pg9184-api-lifetime-budget-host-v1/manifest.safe.json'
HOST_SHA='25e78d19167299a9607096fca250abf66dad05c56a68a054e5a4a0cef6018e68'
MAIN='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetime.java'
UNIT='src/deployment/systemd/schubert-nk-api.service.template'
FORMAL='8b91944df5820535e23ba2469740f1c0aa94c447'
SS='documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md'


def context(rows,text,unit,paths):
    starts=[line for line in unit.splitlines() if line.startswith('ExecStart=')]
    assert len(starts)==1 and starts[0].startswith('ExecStart=!/usr/bin/java ') and ' dev.codex.schubert.nk.batch.file.RootServiceLauncher API' in starts[0]
    assert not any(path.endswith(('.war','.ear','/WEB-INF/web.xml','/META-INF/application.xml','/META-INF/ejb-jar.xml')) for path in paths)
    assert Counter(row['rule'] for row in rows)==Counter(DoNotUseThreads=6,AvoidUsingVolatile=1,CompareObjectsWithEquals=1,EmptyCatchBlock=1)
    assert 'private volatile boolean installed;' in text
    assert 'Thread.currentThread() == owner' in text and 'catch (IllegalStateException shutdownInProgress)' in text
    lines=text.splitlines()
    for row in rows:
        assert row['class']=='ApiProcessLifetime' and row['package']=='dev.codex.schubert.nk.api.bootstrap'
        line=lines[int(row['beginline'])-1]; column=int(row['begincolumn'])-1
        if row['rule']=='DoNotUseThreads': assert line[column:].startswith(('Thread','new Thread'))
        elif row['rule']=='CompareObjectsWithEquals': assert 'Thread.currentThread() == owner' in line
        elif row['rule']=='AvoidUsingVolatile': assert row['variable']=='installed'
        else: assert 'catch (IllegalStateException shutdownInProgress)' in line


def main():
    invocation=capture(Path(__file__));assert not OUT.exists() and host.sha(STATIC)==STATIC_SHA and host.sha(HOST)==HOST_SHA
    raw=json.loads(STATIC.read_bytes());actual=json.loads(HOST.read_bytes())
    assert raw['source']==actual['source']==selected.SOURCE and actual['actualExit']==0
    assert len(actual['cases'])==10 and all(row['result']=='PASS' and not row['nonPass'] for row in actual['cases'])
    names=[]
    for file in (HOST.parent/'xml').glob('TEST-*.xml'):
        assert actual['xmlHashes'][file.name]==host.sha(file)
        for case in ET.parse(file).getroot().findall('testcase'):
            assert not list(case);names.append(case.get('name'))
    assert set(names)=={'lifeBudget'+str(i).zfill(3) for i in range(1,11)}
    for name in ('checkstyle','spotbugs'):
        row=raw['static'][name];assert row['receipt']['actualExit']==0 and row['receipt']['timedOut'] is False and row['findings']==row['processingErrors']==0
    pmd=raw['static']['pmd'];assert pmd['receipt']['actualExit']==4 and pmd['processingErrors']==0 and pmd['findings']==9
    xml=host.W/'pg9183-api-lifetime-budget-static-v1/pmd.xml';assert host.sha(xml)==pmd['reportSha256']
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
    old=subprocess.check_output(['git','show','ecfcbf9f6ab81f77301833eda3fba464c72eb4b5:'+MAIN],cwd=host.ROOT).decode()
    assert 'private volatile boolean installed;' in old and 'catch (IllegalStateException shutdownInProgress)' in old
    decisions=[]
    pending=[]
    for row in parsed:
        if row['rule']=='DoNotUseThreads':
            classification='CONTEXT_NOT_APPLICABLE_J2EE_RULE'
            reason='Vendor J2EE/container-managed thread premise is false for current standalone API jar/approved direct-Java Unit/no WAR/EAR. Current new10 ordinary methods never install hooks/TERM. This applicability review does not qualify legacy hook/native behavior.'
        elif row['rule']=='CompareObjectsWithEquals':
            classification='EXACT_OWNER_THREAD_IDENTITY_REQUIRED'
            reason='Shutdown must avoid waiting for this exact owner Thread object, not name/value equality. Current LIFEBUDGET005/007 exercise owner/cross-owned-fixture notification only, not actual JVM shutdown.'
        else:
            pending.append(dict(raw=row,status='UNCLASSIFIED_LEGACY_LIFECYCLE_HELD',
              sourcePath=MAIN,sourceSha256=digest,reason='Pre-existing installed visibility/Runtime shutdown catch require their own complete contract/legacy-path review; not counted resolved by new10 without hook installation.'))
            continue
        decisions.append(dict(raw=row,classification=classification,reason=reason,sourcePath=MAIN,sourceSha256=digest,
          sourceOrRulesChanged=False,suppressionAdded=False,ordinaryTestWitness='PG9184-api-lifetime-budget-host-v1:LIFEBUDGET001..010_ONLY_LEGACY_HELD'))
    assert len(decisions)==7 and len(pending)==2
    rejected=[]
    for name,rows,source,template,paths in (
      ('unknown-rule',[dict(parsed[0],rule='UNKNOWN'),*parsed[1:]],text,unit,inputs),
      ('container-premise',parsed,text,unit,[*inputs,'unexpected.war']),
      ('wrong-role',parsed,text,unit.replace('ExecStart=!/usr/bin/java ','ExecStart=/usr/bin/caddy ',1),inputs),
      ('identity-lost',parsed,text.replace('Thread.currentThread() == owner','Thread.currentThread().equals(owner)',1),unit,inputs)):
        try: context(rows,source,template,paths)
        except (AssertionError,ValueError): rejected.append(name)
        else: raise AssertionError('invalid partial review accepted')
    verify(invocation);OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=selected.SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      currentHostManifestSha256=HOST_SHA,rawStaticManifestSha256=STATIC_SHA,staticDispositions=decisions,
      unresolvedStaticRows=pending,rawPmd=9,contextNotApplicableJ2ee=6,identityReview=1,
      checkstyle=0,spotbugs=0,unclassified=2,completeStaticDisposition=False,wholeClassStaticAccepted=False,
      unitSha256=inputs[UNIT],formalDesignSource=FORMAL,formalDesignSha256=host.sha(host.ROOT/SS),
      vendorJarSha256=host.sha(vendor),apiJarSha256=api['sha256'],metadataCounterexamples=rejected,
      productTestsExecuted=0,oldSourceResultsTransferred=False,suppressionsAdded=False,
      actualMainNativePt='UNRUN_HOLD',programPtComplete=False,formalUpdated=False,newAccepted=0))
    print(json.dumps(dict(actualExit=0,reviewedPmd=7,unclassified=2,wholeStaticAccepted=False,manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':main()
