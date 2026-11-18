"""Bind the existing exact SSC454 whole scope to the three planned WebLog diagnostics."""
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import re
import runpy

HERE=Path(__file__)
B=runpy.run_path(str(HERE.with_name('5215_g08_four_source_test_ids.py')))
E,D=map(B.get,('E','D'))
read,checked,ref,sha,git=map(B.get,('read','checked','ref','sha','git'))
START=D/'601_WBS66短期実行_20261117/513_P01810WebLog三診断の照合開始.json'
POST=next(E.glob('PG38408*/manifest.json'))
EARLIER=next(E.glob('PG38392*/manifest.json'))
SS=Path('documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md')
TEST=Path('src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/WebLogValueContractTest.java')
ROWS=(
    ('032','ClaimedWebLog','value003ClaimedRowHasAllEightComponentsAndRejectsEachInvalidBoundary',
     'PT-WLOG-VALUE003','ClaimedWebLog[identity/payload/lease=<redacted>]'),
    ('033','EncryptedWebLogPayload','value002CiphertextOwnershipBoundsAndArrayReferenceEqualityRemainExplicit',
     'PT-WLOG-VALUE002','EncryptedWebLogPayload[keyVersion/ciphertext=<redacted>]'),
    ('034','WebLogPayloadIdentity','value001IdentityIsCompleteAndAadMatchesIndependentEightFieldGolden',
     'PT-WLOG-VALUE001','WebLogPayloadIdentity[message/correlation=<redacted>]'),
)


def tool_proofs(post, spec):
    xml=POST.parent
    assert not any(spec[key] for key in ('failed','errors','skipped','notRun'))
    post_file=checked(spec['independentPost'])
    xml=post_file.with_name('original-TEST-junit-jupiter.xml')
    assert ref(xml)['sha256']==post['files'][xml.name]
    root=ET.parse(xml).getroot()
    cases={(t.get('classname'),t.get('name')) for t in root.findall('testcase')}
    assert len(cases)==post['tests']==7 and len(root.findall('testcase'))==7
    assert not any(t.find(k) is not None for t in root.findall('testcase') for k in ('failure','error','skipped'))
    exec_file=checked(spec['sameSingleExec'])
    assert ref(exec_file)['sha256']==post['files']['jacoco.exec']
    return ref(xml),ref(exec_file),cases


def raw_methods(spec,post):
    lines=[line.split('\t') for line in checked(spec['raw']).read_text().splitlines()]
    classes={}
    methods={}
    for row in lines:
        if row[0]=='CLASS':
            classes[row[1]]=(row[2],row[3]=='true')
        if row[0]=='METHOD' and row[2]=='toString':
            methods[row[1]]={kind:dict(missed=int(miss),covered=int(hit))
                             for kind,miss,hit in (counter.split(':') for counter in row[5:])}
    assert len(classes)==9
    assert all(post['classIds'][name]==crc for name,(crc,observed) in classes.items() if observed)
    return classes,methods


def main():
    start=read(START)
    v=start['values']
    source=v['source']
    assert git('rev-parse','HEAD').decode().strip()==source
    plan_path,old_path,trace=map(checked,v['oracleReferences'])
    plans={x['plannedCaseId']:x for x in read(plan_path)}
    old=read(old_path)
    assert old['actualExit']==0 and old['technical']['tests']==5 and not old['whole451Accepted']
    assert read(trace)['mappedTestIds']==21
    spec=read(POST)
    post=read(checked(spec['independentPost']))
    assert post['source']==spec['source'] and post['actualExit']==spec['actualExit']==0
    assert post['completeSourceComponentFour100'] and spec['targetRawAllFive100']
    assert not post['oldExecCombined'] and not post['manualCoverageExclusions']
    assert post['actualBackendNativeFsRootOrHeldClassActions']==0
    assert len(post['inputHashes'])==15
    for name,pin in post['inputHashes'].items():
        assert sha(git('show',f'{post["source"]}:{name}'))==pin
        assert sha(git('show',f'{source}:{name}'))==pin and ref(Path(name))['sha256']==pin
    for name,pin in post['dependencies'].items():
        assert ref(Path(name))['sha256']==pin
    assert len(post['dependencies'])==2
    xml,exec_,cases=tool_proofs(post,spec)
    classes,methods=raw_methods(spec,post)
    old_due={x['catalogId']:x for x in read(EARLIER)['rows']}
    spec_file=Path('evidence/01_PT/018_NK-OPS-001/4569_SSC454Web値診断固定化・単体テスト仕様書.md')
    original=Path('evidence/01_PT/018_NK-OPS-001/4339_WebLog値契約通常五仕様.md')
    main_ref=git('rev-parse','origin/main').decode().strip()
    txt=git('show',f'{main_ref}:{SS}')
    assert b'SSC454' in txt or b'SSC-454' in txt
    actual_fixtures=TEST.read_text()
    rows=[]
    for index,name,fun,tid,literal in ROWS:
        cid='PT-P01810-CATALOG-'+index
        case=plans[cid]
        assert Path(case['source']).name==name+'.java' and case['fixtureAdmission'].startswith('CANDIDATE_')
        assert (f'dev.codex.schubert.nk.web.logging.{TEST.stem}',fun+'()') in cases
        body=actual_fixtures.split(f'void {fun}(',1)[1].split('\n  @Test',1)[0]
        assert literal in body and 'assertEquals(' in body
        assert ('return "'+literal+'";') in Path(case['source']).read_text()
        desc='dev/codex/schubert/nk/web/logging/'+name
        crc,observed=classes[desc]
        counters=methods[desc]
        assert observed and post['classIds'][desc]==crc
        assert counters['METHOD']==dict(missed=0,covered=1) and counters['LINE']==dict(missed=0,covered=1)
        assert counters['INSTRUCTION']==dict(missed=0,covered=2)
        assert (tid in spec_file.read_text() or tid in ('PT-WLOG-VALUE001','PT-WLOG-VALUE003'))
        rows.append(dict(id=cid,testId=tid,method=fun,main=ref(Path(case['source'])),test=ref(TEST),
            independentExpected=literal,oldDecision=ref(EARLIER),
            oldRunScopeQualified=old_due[cid].get('historicalWholeSuiteReused',False),
            rawMethod=counters,physicalCrc=crc,approvedDesign=main_ref))
    target=E/v['run']/'manifest.json'
    value=dict(actualExit=0,head=source,sourceByteScope=15,currentProductionCore=v['productionCoreMain'],
        originalActualSource=post['source'],sameRun=post['run'],fixedDiagnosticRows=rows,design=dict(path=str(SS),commit=main_ref,sha256=sha(txt)),
        approvedPlainFixture=[ref(spec_file),ref(original)],currentApplicableRows=3,originalWholeTests=7,
        originalIndependent=ref(POST),originalXml=xml,originalExec=exec_,newProductTests=0,
        codeChanges=0,oldFiveUnion=False,rawCounterUnion=False,actualSinkOrKeyActions=0,
        whole451Accepted=False,wholeP01810Accepted=False,newAcceptance=0,verifier=ref(HERE),
        terminalAtUTC=datetime.now(timezone.utc).isoformat())
    with target.open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    print(ref(target))


if __name__=='__main__':
    main()
