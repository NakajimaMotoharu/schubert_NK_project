"""Non-numbered method names: explicit existing oracle references and independent static golden."""
import datetime as dt
import json
from pathlib import Path
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

ROOT=data.ROOT;BASE=data.BASE;SOURCE=data.SOURCE
OUT=BASE/'PG9618-header8-oracle-trace-v1'
SPEC=ROOT/'evidence/01_PT/018_NK-OPS-001/1952_G13Header8_非token名・既存oracle対応仕様.md'
SPEC_SHA='ac4863b34625335ee2522ab8dc2403577026af96429d547718369cd9087ac733'
REVIEW=ROOT/'evidence/01_PT/018_NK-OPS-001/1953_G13Header8_独立期待値・golden意味対応表.md'
REVIEW_SHA='c1c859e422dfd954f80fbd2d81b68b848d502e58f46a3ec11469b5f41421b424'
CANON='8b91944df5820535e23ba2469740f1c0aa94c447'
DESIGNS={
 'documents/200_UI/230_インターフェース/232_固定長電文共通仕様.md':'e2092eb5e02855734bf7faec37abcee5d918de3b7fa689e7ae1a9f4b81228288',
 'documents/300_SS/320_メッセージング/322_固定長電文codec実装設計.md':'f6dcecf979d9dbac0338aae079d5730f97ba53afaa3dd46db3e20ef49b21618d'}
ORACLES={
 'P1':('evidence/01_PT/001_NK-PRO-001/001_NK-PRO-001_単体テスト仕様書.md','503c5f6be3caaa341dcec35cb1bd1b8a3892d270bf6a7fa91cdad580b43abdbe'),
 'P104':('evidence/01_PT/001_NK-PRO-001/104_Header契約個別照合・独立反例仕様.md','39f98ffe329d5f58cc8a4df1b68e96ec860c58a56f59995f5f469e66834d80e0'),
 'P108':('evidence/01_PT/001_NK-PRO-001/108_Header共通契約・現source個別受入.md','84afedf2d26539f0e26b2d4d2a9be2d8c7a84f501925db11dbde3728a2a9e4b7'),
 'P2':('evidence/01_PT/002_NK-PRO-002/001_NK-PRO-002_単体テスト仕様書.md','210282dee66ff779a910012781910b3253591da96d23449c4e8d6922a643d59e')}

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    assert data.sha(SPEC.read_bytes())==SPEC_SHA and data.sha(REVIEW.read_bytes())==REVIEW_SHA
    assert subprocess.check_output(['git','rev-parse','origin/main'],cwd=ROOT,text=True).strip()==CANON
    design_text={}
    for path,digest in DESIGNS.items():
        raw=subprocess.check_output(['git','show',CANON+':'+path],cwd=ROOT);assert data.sha(raw)==digest;design_text[path]=raw.decode()
    original={}
    for label,(path,digest) in ORACLES.items():
        raw=(ROOT/path).read_bytes();assert data.sha(raw)==digest;original[label]=raw.decode().splitlines()
    normal=data.read_checked(BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json',data.PINS['normal'][1])
    manifest=data.read_checked(BASE/'PG9592-current-test-method-post-v1/manifest.json','d73ffe203a58ca9fab7f19f0b4baa7b2588fb25ad7e13c75c0c6411f5a719a18')
    methods=data.read_checked(BASE/'PG9592-current-test-method-post-v1/method-declaration-bindings.json',manifest['bindingsSha256'])
    rows=[];hashes={}
    for number,line in enumerate(REVIEW.read_text().splitlines(),1):
        if not line.startswith(('| HeaderModelTest |','| MessageCodecTest |')):continue
        _,kind,name,ids,basis,scope,_=line.split('|');kind=kind.strip();name=name.strip();ids=[s.strip() for s in ids.split(',')]
        observed=[r for r in methods if r['className'].rpartition('.')[2]==kind and r['method']==name];assert len(observed)==1
        method=observed[0];path=method['path'];hashes[path]=normal['begin']['inputHashes'][path]
        assert method['sourceSha256']==hashes[path] and method['compiledDescriptor']=='()V'
        references=[]
        for test_id in ids:
            label='P104' if test_id.startswith('PT-PRO-HDR3266-') else ('P2' if test_id.startswith('PT-PRO-002-') else 'P1')
            matches=[(i,t) for i,t in enumerate(original[label],1) if t.startswith('| '+test_id+' |') or t.startswith(test_id+'：')]
            assert len(matches)==1;i,text=matches[0]
            references.append(dict(existingTestId=test_id,path=ORACLES[label][0],sha256=ORACLES[label][1],line=i,rowSha256=data.sha(text.encode())))
        rows.append(dict(methodDeclarationKey=method['methodDeclarationKey'],sourcePath=path,sourceSha256=hashes[path],
          startLine=method['startLine'],endLine=method['endLine'],compiledDescriptor='()V',physicalTestClassSha256=method['physicalClassSha256'],
          fileCanonicalOwner=method['fileCanonicalOwner'],fileCanonicalCostOwner=method['fileCanonicalCostOwner'],traceCostOwner='WBS-G13.07',
          oracleReferences=references,parentReviewLine=number,parentReviewRowSha256=data.sha(line.encode()),
          independentExpectedBasis=basis.strip(),applicabilityAndLimits=scope.strip(),
          reviewStatus='STATIC_METHOD_ORACLE_RELATION_REVIEWED_NOT_DYNAMIC_PT',oldDynamicResultsTransferred=False,productExecuted=False))
    assert len(rows)==8 and len({r['methodDeclarationKey'] for r in rows})==8
    graph=data.read_checked(BASE/'PG9386-composite-reference-graph-v3/manifest.json',data.PINS['graph'][1])
    mains=data.read_checked(BASE/'PG9386-composite-reference-graph-v3/main-class-sources.json',graph['mainMapSha256'])
    selected={}
    for name in ('AuthenticationContext','CommonHeader','MessageKind','InteractionKind','ResultCode','HeaderCodec'):
        package='codec' if name=='HeaderCodec' else 'header';key='dev/codex/schubert/nk/protocol/'+package+'/'+name
        selected[key]=mains[key];path=mains[key]['path'];hashes[path]=normal['begin']['inputHashes'][path]
        assert mains[key]['owner']==('WBS-P002-03' if name=='HeaderCodec' else 'WBS-P001-01')
    for p,h in hashes.items():assert data.sha((ROOT/p).read_bytes())==data.sha((data.NORMAL/p).read_bytes())==h
    fields=[]
    for line in REVIEW.read_text().splitlines():
        cells=[x.strip() for x in line.split('|')[1:-1]]
        if len(cells)==5 and cells[0].isdigit():fields.append(dict(number=int(cells[0]),uiStart=int(cells[1]),length=int(cells[2]),offset=int(cells[3]),meaning=cells[4]))
    assert [r['number'] for r in fields]==list(range(1,18)) and sum(r['length'] for r in fields)==256
    expected=bytearray(b' '*256);uuid='123e4567-e89b-12d3-a456-426614174000'
    values={1:'SCHBNK01',2:'001',3:'LGNREQ01',4:'001',5:'Q',6:'S',7:uuid,8:uuid,9:'20260902123456789',
      11:'0256',12:'000384',13:'000000',14:'000000',15:'000000640'}
    end=0
    for field in fields:
        assert field['uiStart']-1==field['offset']==end;end+=field['length']
        value=values.get(field['number'],' '*field['length']).encode('ascii');assert len(value)==field['length']
        expected[field['offset']:end]=value
    golden=next(r for r in rows if 'MessageCodecTest#' in r['methodDeclarationKey'])
    lines=(ROOT/golden['sourcePath']).read_text().splitlines();body='\n'.join(lines[golden['startLine']-1:golden['endLine']])
    assert "Arrays.fill(expected, (byte) ' ');" in body and 'new byte[256]' in body
    actual=bytearray(b' '*256);assignments=re.findall(r'ascii\(expected,\s*([0-9]+),\s*("[^"\r\n]*"|MESSAGE_ID\.toString\(\))\)',body)
    assert len(assignments)==13
    for offset,text in assignments:
        value=(uuid if text=='MESSAGE_ID.toString()' else json.loads(text)).encode('ascii');at=int(offset)
        assert 0<=at<=256-len(value);actual[at:at+len(value)]=value
    assert actual==expected and end==256 and 256+384==640 and 1_000_000-256==999_744
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    verify(invocation);OUT.mkdir();data.write(OUT/'method-oracle-review.json',rows);data.write(OUT/'golden-field-map.json',fields)
    result=dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      specSha256=SPEC_SHA,reviewSha256=REVIEW_SHA,oracleDocuments=ORACLES,canonicalDesignCommit=CANON,canonicalDesignHashes=DESIGNS,
      sourceHashes=hashes,reviewedCurrentMainClasses=selected,methodsReviewed=8,existingDistinctTestIdFamilies=6,methodTestIdRelations=9,
      methodOracleReviewSha256=data.sha((OUT/'method-oracle-review.json').read_bytes()),goldenFieldMapSha256=data.sha((OUT/'golden-field-map.json').read_bytes()),
      uiFields=17,testBuilderAssignments=13,staticGoldenReconstructionSha256=data.sha(bytes(expected)),staticGoldenEqualsTestBuilder=True,
      actualProductionEncodingExecuted=False,productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalUpdated=False,newAccepted=0,
      effortPercent=None,wholeG13Accepted=False,whole451Accepted=False,reviewDoesNotProveAllQseOrLayouts=True)
    data.write(OUT/'manifest.json',result)
    print(json.dumps(dict(actualExit=0,methodsReviewed=8,uiFields=17,productTestsExecuted=0)))
    print('manifestSha256='+data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
