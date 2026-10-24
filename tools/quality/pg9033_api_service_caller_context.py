"""Current two raw J2EE-premise findings reviewed against actual source/vendor/formal design."""
import copy
import datetime as dt
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from host_tool_invocation import capture,verify
from public_blob_scan import sha

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9033-api-service-caller-context-v1'
RAW=BASE/'PG9031-api-service-caller-static-v1/manifest.json'
RAW_SHA='1dab5cae1970063d2cabbe329b45556ada50b53803fb1d1fd8aba2220d93c90e'
SOURCE='73d94fc525c6ea8828ca82d906ec583146fee7bf'
MAIN='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiProcessMain.java'
UNIT='src/deployment/systemd/schubert-nk-api.service.template'
FORMAL='8b91944df5820535e23ba2469740f1c0aa94c447'
SS='documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md'


def context(raw,source,unit,paths,original):
    starts=[line for line in unit.splitlines() if line.startswith('ExecStart=')]
    assert len(starts)==1 and starts[0].startswith('ExecStart=!/usr/bin/java ')
    assert ' dev.codex.schubert.nk.batch.file.RootServiceLauncher API' in starts[0]
    assert not any(name.endswith(('/WEB-INF/web.xml','/META-INF/application.xml','/META-INF/ejb-jar.xml','.war','.ear')) for name in paths)
    assert len(raw)==len(original)==2
    lines=source.splitlines()
    for row,prior in zip(raw,original,strict=True):
        assert row==prior['raw'] and row['rule']=='DoNotUseThreads'
        span=lines[int(row['beginline'])-1:int(row['endline'])]
        assert span==prior['sourceSpan']


def main():
    invocation=capture(Path(__file__));assert not OUT.exists() and sha(RAW.read_bytes())==RAW_SHA
    raw=json.loads(RAW.read_bytes());assert raw['source']==SOURCE and raw['actualExit']==1
    assert raw['static']['pmd']['processingErrors']==0 and raw['static']['pmd']['findings']==2
    assert raw['static']['checkstyle']['findings']==raw['static']['spotbugs']['findings']==0
    manual=BASE/'PG8880-caller-static-manual-v1/decisions.json'
    assert sha(manual.read_bytes())=='b83db3d949a6ab3e44ad810e4b304b6aec0cc06ef7327dfd04858a0116a0addf'
    old=[row for row in json.loads(manual.read_bytes())['rows'] if row['role']=='api']
    normal=json.loads((BASE/'PG9028-api-service-six-compile-v1/manifest.json').read_bytes())
    hashes=normal['begin']['inputHashes'];source=(ROOT/MAIN).read_text();unit=(ROOT/UNIT).read_text()
    assert sha(source.encode())==hashes[MAIN]==raw['sourceHashes'][MAIN] and sha(unit.encode())==hashes[UNIT]
    context(raw['static']['pmd']['rawFindings'],source,unit,hashes,old)
    formal=subprocess.check_output(['git','show',FORMAL+':'+SS],cwd=ROOT)
    assert sha(formal)=='3775cb1faf0b96572f4913d06682100da1861f1d364a66f4118b03e27abf4b82'
    assert all(word in formal.decode() for word in ('API','java','systemd'))
    vendor=ROOT.parent/'toolchain/static-gates-20261015/pmd-bin-7.28.0/lib/pmd-java-7.28.0.jar'
    assert sha(vendor.read_bytes())==raw['toolHashes'][str(vendor)]=='068b2b5fb276559c32d52e3675d297a458bf27fe181b675cee10555a55c131bd'
    with zipfile.ZipFile(vendor) as archive:rules=ET.fromstring(archive.read('category/java/multithreading.xml'))
    rule=[row for row in rules.findall('{*}rule') if row.get('name')=='DoNotUseThreads'];assert len(rule)==1
    premise=' '.join(''.join(rule[0].find('{*}description').itertext()).split());assert 'J2EE' in premise and 'managed' in premise
    rejected=[]
    cases=[('not-direct-java',raw['static']['pmd']['rawFindings'],source,unit.replace('ExecStart=!/usr/bin/java ','ExecStart=/usr/bin/caddy ',1),hashes),
           ('war-role',raw['static']['pmd']['rawFindings'],source,unit,{**hashes,'example.war':'0'*64}),
           ('changed-source-subject',raw['static']['pmd']['rawFindings'],source.replace('Thread.currentThread().setUncaughtExceptionHandler','Thread.ofPlatform().setUncaughtExceptionHandler',1),unit,hashes)]
    changed=copy.deepcopy(raw['static']['pmd']['rawFindings']);changed[0]['rule']='OtherRule'
    cases.append(('wrong-rule',changed,source,unit,hashes))
    for name,rows,text,template,inputs in cases:
        try:context(rows,text,template,inputs,old)
        except AssertionError:rejected.append(name)
        else:raise AssertionError('rule premise mismatch accepted')
    verify(invocation);OUT.mkdir()
    decisions=[]
    for row,prior in zip(raw['static']['pmd']['rawFindings'],old,strict=True):
        decisions.append(dict(raw=row,currentSourceSha256=hashes[MAIN],sourceSpan=prior['sourceSpan'],
              status='CONTEXT_NOT_APPLICABLE_J2EE_RULE',reason=prior['reason'],counterexample=prior['counterexample'],
              rawWarningRetained=True,sourceChangedByReview=False,currentDynamicPt='UNRUN_HOLD',currentCoverage=None))
    value=dict(actualExit=0,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,source=SOURCE,
        rawStaticManifestSha256=RAW_SHA,rawStaticExit=1,rawPmdExit=4,rawFindings=2,
        sourceHash=hashes[MAIN],unitTemplateSha256=hashes[UNIT],formalDesignCommit=FORMAL,formalDesignSha256=sha(formal),
        vendorJarSha256=sha(vendor.read_bytes()),rulePremiseSha256=sha(premise.encode()),decisions=decisions,
        applicabilityUnclassified=0,applicableViolations=0,rejectedMetadataCases=rejected,
        oldGroundsRecheckedNotOldPtTransferred=True,suppressionsAdded=False,qualityGatePass=False,
        productTestsExecuted=0,coverage=None,ptExecutionExempt=False,whole451Accepted=False,formalUpdated=False,newAccepted=0)
    with (OUT/'manifest.json').open('x',encoding='utf-8') as stream:
        json.dump(value,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,rawPmd=2,contextNotApplicable=2,applicabilityUnclassified=0,qualityGatePass=False)))


if __name__=='__main__':main()
