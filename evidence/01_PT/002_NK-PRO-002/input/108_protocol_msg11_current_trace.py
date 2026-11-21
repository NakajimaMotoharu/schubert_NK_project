import hashlib,json,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
ops=Path('evidence/01_PT/018_NK-OPS-001/evidence')
def git(*args):
    return subprocess.check_output(['git',*args])
def pin(path):
    return dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
def read(path):
    return json.loads(path.read_bytes())
def run_file(n,name='manifest.json'):
    return next(ops.glob('PG'+str(n)+'*/'+name))
authority='ee27a308b6b7da7bd9744000ee490a8f91956ead'
assert git('rev-parse','origin/main').decode().strip()==authority
rd=next(Path('documents/100_RD').glob('*/132_*.md'))
ss=next(Path('documents/300_SS').glob('*/322_*.md'))
design=[dict(path=str(p),sha256=hashlib.sha256(git('show',f'{authority}:{p}')).hexdigest()) for p in (rd,ss)]
requirements=dict(re.findall(r'^\| (MSG-\d{3}) \| (.+?) \|$',git('show',f'{authority}:{rd}').decode(),re.M))
assert set(requirements)=={f'MSG-{i:03}' for i in range(1,12)}
assert '### 6.2 N' in git('show',f'{authority}:{ss}').decode()
partial=read(run_file(41394))
old=run_file(26250,'requirement-oracle-matrix.json')
old_rows={r['requirementId']:r for r in read(old) if r['requirementId'] in requirements}
assert set(old_rows)==set(requirements)
roster=run_file(41304,'cases.json')
assert partial['originalRoster']==pin(roster.resolve())
outcomes={(r['className'].rsplit('.',1)[-1],r['method']):r for r in read(roster)}
assert len(outcomes)==171
branch=git('rev-parse','HEAD').decode().strip()
target=Path('src/schubert-nk-protocol')
assert not git('diff','--name-only',partial['qualifiedProtocolSource'],branch,'--',str(target),'pom.xml','tools/quality/static')
extra={
 'MSG-004':[('FieldCodecTest','numericDecodeValidatesEveryByteBeforeAccumulatingTheValue','PT-PRO-002-N03',
             'ASCII grammar precedence on fixed signed-long overflow body with 0x2b and 0xff; fixed error and blank cause.')],
 'MSG-007':[('FieldCodecTest','textEncodeNormalizesUtf8AndPadsWithAsciiSpace','PT-PRO-CURRENT-MSG-003',
             'Four-byte scalar plus ASCII x cannot fit in four bytes; FieldEncodingException without truncation.')],
 'MSG-011':[('JstWireTimestampTest','formatsAndParsesStrictJstMilliseconds',None,
             'Exact independent JST millisecond text and UTC inverse on the original method.')],
}
residual={
 'MSG-001':'実JMS送受信・adapter／実CHR',
 'MSG-007':'実送信側で非送信・DB不変更が成立する同候補経路',
 'MSG-009':'全製品・設定・文書・生成物のLF一括確認',
 'MSG-011':'実時計・外部経路の時点規定、QA060固有の履歴時刻は別契約',
}
def test_entry(unit,method,test_id,basis):
    r=outcomes[(unit,method)]
    assert r['outcome']=='PASS'
    path=target/'src/test/java'/Path(r['className'].replace('.','/')+'.java')
    source=git('show',f'{partial["qualifiedProtocolSource"]}:{path}')
    assert source==path.read_bytes() and ('void '+method+'(').encode() in source
    return dict(case=r['className']+'#'+method,testId=test_id,expectedBasis=basis,fixture=pin(path),actual='PASS_ORIGINAL')
rows=[]
for ident in sorted(requirements):
    prev=old_rows[ident]
    unit,method=prev['case'].split('#',1)
    points=[test_entry(unit,method,prev['testId'],prev['independentExpectedBasis'])]
    for add in extra.get(ident,[]):
        points.append(test_entry(*add))
    rows.append(dict(requirementId=ident,requirement=requirements[ident],testEvidence=points,confirmed='CURRENT_HOST_COMPONENT_ONLY',
        residual=residual.get(ident,'当候補の終了依存、実CHRと451の該当全品質')))
out=ops/'PG41396-protocol-msg11-exact-trace-v1'
out.mkdir()
result=dict(run=out.name,actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),
    source=branch,physicalScope=pin(run_file(41394)),productionCore=partial['productionCore'],
    qualifiedProtocolSource=partial['qualifiedProtocolSource'],canonicalDesign=authority,design=design,
    retainedCases=pin(roster),historicalTrace=pin(old),rows=rows,requirementsVerified=11,extraCurrentTraceReferences=3,
    testExecutions=0,externalActions=0,formalDelta=0,restored=0,whole451=False)
(out/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(len(rows),result['extraCurrentTraceReferences'])
