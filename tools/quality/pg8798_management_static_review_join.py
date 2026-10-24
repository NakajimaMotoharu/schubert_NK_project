"""Exact40 individual manual applicability/source join, no Production execution or PT exemption."""
from collections import Counter
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile
import pg8791_management_metric_static as static
from host_tool_invocation import capture,verify

host=static.host
SOURCE=static.selected.SOURCE
FORMAL='8b91944df5820535e23ba2469740f1c0aa94c447'
MANUAL=host.BASE/'PG8797-management-static-manual-review-v1/decisions.json'
MANUAL_SHA='ba2a09cb954c8b07daee1ab0e3dfbb0f9d7b71c270b60a828ddb60a81b3bbb77'
ORIGIN=host.BASE/'PG8793-management-metric-finding-origin-v1/manifest.json'
ORIGIN_SHA='3b42b90552d2d8e6d91a3cfe805b2bda38398600dcb3028a701680d24f82cf36'
STATIC=host.BASE/'PG8791-management-metric-static-v1/manifest.json'
STATIC_SHA='a90c75594c92df4ff73aa017a1a6c72eb152b97d32cdbc5df603b02e53990a47'
SLOT=host.W/'pg8798-management-static-review-join-v1'
OUT=host.BASE/'PG8798-management-static-review-join-v1'
SS342='documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md'

def canonical(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()

def validate(manual,origin):
    assert manual['schema']=='PGPT_INDIVIDUAL_PMD40_SOURCE_REVIEW_V1'
    assert manual['source']==origin['source']==SOURCE and manual['formalDesignCommit']==FORMAL
    assert manual['rawManifestSha256']==STATIC_SHA and manual['originManifestSha256']==ORIGIN_SHA
    assert manual['reviewedRawRows']==40 and manual['uniqueRawDiagnostics']==36
    assert manual['productTestsExecuted']==0 and manual['coverage'] is None and manual['formalUpdated'] is False
    assert len(manual['rows'])==len(origin['findings'])==40
    assert [row['index'] for row in manual['rows']]==list(range(1,41))
    for row,original in zip(manual['rows'],origin['findings'],strict=True):
        assert all(row[key]==original[key] for key in ('index','path','sourceSha256','raw'))
        assert row['rawWarningRetained'] is True and row['sourceChangedByReview'] is False
        assert row['qualityGatePass'] is False and row['actualRuntimeProven'] is False and row['formalAccepted'] is False and row['ptAlternativeCompleted']==0
        assert len(row['reason'])>=100 and len(row['counterexample'])>=50 and row['subject']
        assert row['design']==['RD171','UI252','SS342 SSC312/313/317/335','SS351','411/451']
        assert row['reviewPasses']==['RULE_TO_APPROVED_CONTRACT','COUNTEREXAMPLE_SOURCE_RECHECK'] and row['reviewOwner']=='PGPT_PARENT'
        assert row['reviewExpires']=='ANY_RELEVANT_SOURCE_OR_APPROVED_CONTRACT_CHANGE'
        assert row['status']==('CONTEXT_NOT_APPLICABLE_J2EE_RULE' if row['raw']['rule']=='DoNotUseThreads' else 'REQUIRED_CONTRACT_CURRENT_PT_JOIN_PENDING')
        test=row['testReference']
        assert test['currentRunStatus']=='UNRUN_HOLD_REFERENCE_ONLY' and test['currentXmlQualified'] is False
        assert test['path'].startswith('src/schubert-nk-') and test['path'].endswith('/'+test['className'].rsplit('.',1)[1]+'.java')
        assert test['className'].endswith('Test') and test['method']
    assert len({canonical(row['raw']) for row in manual['rows']})==36
    counts=Counter(row['status'] for row in manual['rows'])
    assert counts==Counter(CONTEXT_NOT_APPLICABLE_J2EE_RULE=21,REQUIRED_CONTRACT_CURRENT_PT_JOIN_PENDING=19)
    return dict(counts)

def main():
    invocation=capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    for file,digest in ((MANUAL,MANUAL_SHA),(ORIGIN,ORIGIN_SHA),(STATIC,STATIC_SHA)):
        assert host.sha(file)==digest
    manual,origin,analysis=[json.loads(file.read_text()) for file in (MANUAL,ORIGIN,STATIC)]
    statuses=validate(manual,origin)
    assert analysis['actualExit']==1 and analysis['static']['pmd']['findings']==40 and analysis['unclassified']==40
    assert host.sha(static.selected.COMPILE/'manifest.safe.json')==static.selected.COMPILE_SHA
    normal=json.loads((static.selected.COMPILE/'manifest.safe.json').read_text())
    assert normal['source']==SOURCE and normal['actualExit']==normal['terminal']['actualExit']==0 and normal['testsExecuted']==0
    inputs=normal['begin']['inputHashes']
    assert all(host.sha(host.ROOT/path)==digest for path,digest in inputs.items())
    pmd=static.SLOT/'pmd.xml'
    assert host.sha(pmd)==analysis['static']['pmd']['reportSha256']
    parsed=[];xml_paths=[]
    for file in ET.parse(pmd).getroot().findall('{*}file'):
        path=Path(file.attrib['name']).relative_to(host.ROOT).as_posix()
        for node in file.findall('{*}violation'):
            parsed.append(dict(node.attrib,message=' '.join(''.join(node.itertext()).split())))
            xml_paths.append(path)
    assert parsed==[row['raw'] for row in manual['rows']]
    assert xml_paths==[row['path'] for row in manual['rows']]
    declarations={};source_facts={}
    for role,path in static.MAIN.items():
        body=(host.ROOT/path).read_text();compact=''.join(body.split())
        assert inputs[path]==analysis['sourceHashes'][path]==host.sha(host.ROOT/path)
        assert 'newThreadPoolExecutor(1,1,0,TimeUnit.MILLISECONDS,newArrayBlockingQueue<>(32),' in compact
        assert 'thread.setDaemon(true)' in compact and 'executor.shutdownNow();' in compact and 'executor.awaitTermination(' in compact
        assert 'catch(RuntimeException|Errorfailure)' in compact and 'catch(RuntimeException|Errorunconfirmed)' in compact
        assert 'if(unconfirmedinstanceofError&&!(failureinstanceofError))throwunconfirmed;' in compact
        assert 'if(unconfirmed!=failure)failure.addSuppressed(cleanupDiagnostic);' in compact
        if role=='web':
            assert 'privatevolatilebooleanstarted;' in compact and compact.count('started=true;')==1
            assert compact.index('server.start();')<compact.index('started=true;')
            assert 'returnstarted&&!stopping.get()&&promoted.get()&&healthy.getAsBoolean();' in compact
            assert 'if(entryInterrupted)Thread.currentThread().interrupt();' in compact
        else:
            assert 'booleaninterrupted=Thread.interrupted();' in compact and 'if(interrupted)Thread.currentThread().interrupt();' in compact
        unit=f'src/deployment/systemd/schubert-nk-{role}.service.template'
        text=(host.ROOT/unit).read_text()
        assert inputs[unit]==host.sha(host.ROOT/unit)
        lines=[line for line in text.splitlines() if line.startswith('ExecStart=')]
        assert len(lines)==1 and lines[0].startswith('ExecStart=!/usr/bin/java ') and ' dev.codex.schubert.nk.batch.file.RootServiceLauncher '+role.upper() in lines[0]
        assert all(not name.endswith(('/WEB-INF/web.xml','/META-INF/application.xml','/META-INF/ejb-jar.xml','.war','.ear')) for name in inputs)
        source_facts[role]=dict(path=path,sha256=inputs[path],unitTemplate=unit,unitSha256=inputs[unit],approvedModel='DIRECT_JAVA_STANDALONE_SOURCE_CONTRACT_NOT_CURRENT_DEPLOYMENT_PROOF',noManagedDescriptorsInFrozenInput=True,fixedPoolBeforeHttp=True)
    for row in manual['rows']:
        reference=row['testReference'];path=reference['path']
        assert path in inputs and host.sha(host.ROOT/path)==inputs[path]
        text=(host.ROOT/path).read_text()
        assert 'package '+reference['className'].rsplit('.',1)[0]+';' in text
        assert re.search(r'\bclass\s+'+re.escape(reference['className'].rsplit('.',1)[1])+r'\b',text)
        assert re.search(r'@Test\s+(?:/\*.*?\*/\s*)?void\s+'+re.escape(reference['method'])+r'\(',text,re.S)
        declarations[path]=dict(sha256=inputs[path],runtimeStatus='UNRUN_HOLD_REFERENCE_ONLY',currentXmlQualified=False)
    vendor=host.TC/'static-gates-20261015/pmd-bin-7.28.0/lib/pmd-java-7.28.0.jar'
    assert str(vendor) in analysis['toolHashes'] and host.sha(vendor)==analysis['toolHashes'][str(vendor)]
    with zipfile.ZipFile(vendor) as archive:
        xml=archive.read('category/java/multithreading.xml')
    rules=ET.fromstring(xml)
    selected=[node for node in rules.findall('{*}rule') if node.attrib.get('name')=='DoNotUseThreads']
    assert len(selected)==1
    premise=' '.join(''.join(selected[0].find('{*}description').itertext()).split())
    assert 'J2EE specification explicitly forbids' in premise and 'managed and monitored by the J2EE server' in premise
    formal=subprocess.check_output(['git','show',FORMAL+':'+SS342],cwd=host.ROOT)
    assert all(marker.encode() in formal for marker in ('SSC312','SSC313','SSC317','SSC335','core/max1','queue32','java','systemd'))
    SLOT.mkdir();static.steps.SLOT=SLOT
    java=host.TC/'jdk-25.0.4/bin'
    sdk_receipt,sdk_text=static.steps.step('jdk-throwable-metadata',[str(java/'javap'),'-p','-c','java.lang.Throwable'])
    assert sdk_receipt['actualExit']==0 and not sdk_receipt['timedOut']
    start=sdk_text.index('public final synchronized void addSuppressed(')
    block=sdk_text[start:sdk_text.index('public final synchronized java.lang.Throwable[] getSuppressed(',start)]
    assert 'if_acmpne' in block and 'Self-suppression not permitted' in block
    assert all(host.sha(host.ROOT/path)==digest for path,digest in inputs.items())
    verify(invocation);OUT.mkdir()
    proof=dict(actualExit=0,source=SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,manualReviewSha256=MANUAL_SHA,originManifestSha256=ORIGIN_SHA,staticManifestSha256=STATIC_SHA,pmdReportSha256=host.sha(pmd),normalManifestSha256=static.selected.COMPILE_SHA,rawFindings=40,uniqueRawDiagnostics=36,statusCounts=statuses,unreviewedFindings=0,currentXmlContractJoinPending=19,rawWarningRemoved=0,applicableViolationCount=None,managerStaticWholePass=False,reviewScope='INDIVIDUAL_SOURCE_APPLICABILITY_WITH_PENDING_CURRENT_DYNAMIC_JOIN',rationaleTruth='PARENT_CONTRACT_AND_COUNTEREXAMPLE_REVIEW_NOT_MACHINE_SEMANTIC_PROOF',sourceFacts=source_facts,plannedTestDeclarations=declarations,formalDesign=dict(commit=FORMAL,path=SS342,sha256=hashlib.sha256(formal).hexdigest()),primaryPmdPremise=dict(jarSha256=host.sha(vendor),xmlSha256=hashlib.sha256(xml).hexdigest(),rule='DoNotUseThreads',description=premise),jdkSelfSuppressionMetadata=dict(receipt=sdk_receipt,javapSha256=host.sha(java/'javap'),identityInstruction='if_acmpne',applicationTargetInitialized=False),productTestsExecuted=0,coverage=None,ptAlternativeCompleted=0,F03Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0)
    host.write(OUT/'manifest.json',proof)
    print(json.dumps(dict(actualExit=0,raw40=40,unique36=36,statusCounts=statuses,currentXmlContractJoinPending=19,newProductPt=0,formalUpdated=False,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':
    main()
