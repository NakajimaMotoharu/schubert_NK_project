"""Individual caller15 review/source/vendor premise join only; no Production execution."""
from collections import Counter
import datetime
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile
import pg8870_web_caller_metric_host as selected
from host_tool_invocation import capture,verify

host=selected.run.host
SOURCE=selected.SOURCE
FORMAL='8b91944df5820535e23ba2469740f1c0aa94c447'
MANUAL=host.BASE/'PG8880-caller-static-manual-v1/decisions.json'
MANUAL_SHA='b83db3d949a6ab3e44ad810e4b304b6aec0cc06ef7327dfd04858a0116a0addf'
OUT=host.BASE/'PG8882-caller-static-review-join-v1'
SPECS=[('api','PG8859-api-caller-metric-static-v1','d230ac886953afcfa82fc3b6c78c766263d52d731e4d3c71cef0027d128b358a','src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiProcessMain.java'),('web','PG8873-web-caller-metric-static-v1','8fc80c4cef3c23b217a9ded8ba1b150a857424c10d1345810608241da1a1f532','src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebNativeRuntime.java')]
SS342='documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md'

def inputs():
    rows=[];analyses={}
    for role,folder,digest,path in SPECS:
        file=host.BASE/folder/'manifest.json'
        assert host.sha(file)==digest
        analysis=json.loads(file.read_text());analyses[role]=analysis
        assert analysis['actualExit']==1 and analysis['static']['pmd']['processingErrors']==0
        assert analysis['static']['checkstyle']['findings']==analysis['static']['spotbugs']['findings']==0
        assert host.sha(host.ROOT/path)==analysis['sourceHashes'][path]
        lines=(host.ROOT/path).read_text().splitlines()
        for raw in analysis['static']['pmd']['rawFindings']:
            rows.append(dict(index=len(rows)+1,role=role,path=path,sourceSha256=analysis['sourceHashes'][path],raw=raw,sourceSpan=lines[int(raw['beginline'])-1:int(raw['endline'])],rawManifest=folder+'/manifest.json',rawManifestSha256=digest,rawSource=analysis['source']))
    assert len(rows)==15
    return rows,analyses

def validate(manual,expected):
    assert manual['schema']=='PGPT_CALLER15_INDIVIDUAL_STATIC_REVIEW_V1'
    assert manual['source']==SOURCE and manual['formalDesignCommit']==FORMAL
    assert manual['reviewedRawRows']==len(manual['rows'])==len(expected)==15 and manual['rawWarningsRetained'] is True
    assert manual['productTestsExecuted']==manual['ptAlternativeCompleted']==0 and manual['coverage'] is None and manual['formalUpdated'] is False
    for row,original in zip(manual['rows'],expected,strict=True):
        assert all(row[key]==value for key,value in original.items())
        assert row['subject']==' '.join(row['sourceSpan']).strip()
        assert row['reviewOwner']=='PGPT_PARENT' and row['reviewPasses']==['RULE_TO_SOURCE_CONTRACT','COUNTEREXAMPLE_SOURCE_RECHECK']
        assert len(row['reason'])>100 and len(row['counterexample'])>50
        assert row['rawWarningRetained'] is True and row['sourceChangedByReview'] is False
        assert row['qualityGatePass'] is row['actualRuntimeProven'] is row['formalAccepted'] is row['currentXmlQualified'] is False and row['ptAlternativeCompleted']==0
        assert row['status']==('CONTEXT_NOT_APPLICABLE_J2EE_RULE' if row['role']=='api' else 'REQUIRED_CONTRACT_DYNAMIC_JOIN_PENDING')
        if row['role']=='api':
            assert row['raw']['rule']=='DoNotUseThreads' and row['testReference'] is None
        else:
            reference=row['testReference']
            assert reference['currentRunStatus']=='UNRUN_HOLD_REFERENCE_ONLY' and reference['currentXmlQualified'] is False
            assert reference['path'].startswith('src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/')
            text=(host.ROOT/reference['path']).read_text()
            assert 'package '+reference['className'].rsplit('.',1)[0]+';' in text
            assert re.search(r'@Test\s+void\s+'+re.escape(reference['method'])+r'\(',text)
    counts=Counter(row['status'] for row in manual['rows'])
    assert counts==Counter(CONTEXT_NOT_APPLICABLE_J2EE_RULE=2,REQUIRED_CONTRACT_DYNAMIC_JOIN_PENDING=13)
    return dict(counts)

def main():
    invocation=capture(Path(__file__))
    assert not OUT.exists() and host.sha(MANUAL)==MANUAL_SHA
    assert host.sha(selected.COMPILE/'manifest.safe.json')==selected.COMPILE_SHA
    normal=json.loads((selected.COMPILE/'manifest.safe.json').read_text())
    assert normal['source']==SOURCE and normal['actualExit']==normal['terminal']['actualExit']==normal['testsExecuted']==0
    expected,analyses=inputs();manual=json.loads(MANUAL.read_text())
    counts=validate(manual,expected)
    hashes=normal['begin']['inputHashes']
    facts={}
    for role,_,_,path in SPECS:
        assert host.sha(host.ROOT/path)==hashes[path]
        unit=f'src/deployment/systemd/schubert-nk-{role}.service.template'
        text=(host.ROOT/unit).read_text();assert host.sha(host.ROOT/unit)==hashes[unit]
        starts=[line for line in text.splitlines() if line.startswith('ExecStart=')]
        assert len(starts)==1 and starts[0].startswith('ExecStart=!/usr/bin/java ') and ' dev.codex.schubert.nk.batch.file.RootServiceLauncher '+role.upper() in starts[0]
        assert not any(name.endswith(('/WEB-INF/web.xml','/META-INF/application.xml','/META-INF/ejb-jar.xml','.war','.ear')) for name in hashes)
        facts[role]=dict(path=path,sha256=hashes[path],unitTemplate=unit,unitSha256=hashes[unit],reviewOnlyNotActualDeployment=True)
    vendor=host.TC/'static-gates-20261015/pmd-bin-7.28.0/lib/pmd-java-7.28.0.jar'
    assert all(analysis['toolHashes'][str(vendor)]==host.sha(vendor) for analysis in analyses.values())
    with zipfile.ZipFile(vendor) as archive: rules=ET.fromstring(archive.read('category/java/multithreading.xml'))
    rule=[node for node in rules.findall('{*}rule') if node.attrib.get('name')=='DoNotUseThreads']
    assert len(rule)==1
    premise=' '.join(''.join(rule[0].find('{*}description').itertext()).split())
    assert 'J2EE specification explicitly forbids' in premise and 'managed and monitored by the J2EE server' in premise
    formal=subprocess.check_output(['git','show',FORMAL+':'+SS342],cwd=host.ROOT)
    current=subprocess.check_output(['git','show','origin/main:'+SS342],cwd=host.ROOT)
    assert formal==current and b'RootServiceLauncher' in formal and b'ExecStart=' in formal
    declarations={r['testReference']['path']:host.sha(host.ROOT/r['testReference']['path']) for r in manual['rows'] if r['testReference']}
    assert all(hashes[path]==digest for path,digest in declarations.items())
    # PG source only: field capture/phase order and outer failure-frame retention.
    web=(host.ROOT/SPECS[1][3]).read_text();compact=''.join(web.split())
    assert 'privatefinalObjectownerLock=newObject();' in compact and compact.count('synchronized(ownerLock)')==2
    assert compact.index('varvalue=management;')<compact.index('varvalue=metrics;')<compact.index('varvalue=assets;')
    execution='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebRuntimeExecution.java'
    ex=(host.ROOT/execution).read_text();assert host.sha(host.ROOT/execution)==hashes[execution]
    assert 'finally' in ex and 'close.run();' in ex and 'while (true)' in ex and 'Reference.reachabilityFence(close);' in ex
    verify(invocation);OUT.mkdir()
    value=dict(actualExit=0,source=SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,manualSha256=MANUAL_SHA,sourceFacts=facts,rawStaticPins=[dict(role=r[0],path=r[1]+'/manifest.json',sha256=r[2]) for r in SPECS],counts=counts,reviewedRawRows=15,reviewUnclassified=0,rawOriginalStaticExit=1,rulePremise=dict(vendorJarSha256=host.sha(vendor),description=premise),formalDesign=dict(commit=FORMAL,path=SS342,sha256=__import__('hashlib').sha256(formal).hexdigest()),testDeclarations=declarations,sourceFactsNotCurrentRuntime=True,qualityGatePass=False,coverage=None,productTestsExecuted=0,ptAlternativeCompleted=0,formalUpdated=False,newAccepted=0,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0)
    host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,counts=counts,productPtExecuted=0,qualityGatePass=False,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':
    main()
