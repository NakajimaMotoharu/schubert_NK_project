"""Independent canonical UI positions and frozen method/spec references, not encoder execution."""
from collections import Counter
import copy
import datetime as dt
import json
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

ROOT=data.ROOT;BASE=data.BASE;SOURCE=data.SOURCE
SUBJECT=BASE/'PG9618-header8-oracle-trace-v1'
SUBJECT_SHA='31cd0d1ea0ae26cd364fae679de4093304d305bc69e001c1254c8af31b175317'
OUT=BASE/'PG9620-header8-oracle-post-v1'

def validate(actual,expected):
    if actual!=expected:raise ValueError('exact current method, original oracle and canonical UI bounds required')

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    primary=data.read_checked(SUBJECT/'manifest.json',SUBJECT_SHA);assert primary['actualExit']==0 and primary['source']==SOURCE
    records=data.read_checked(SUBJECT/'method-oracle-review.json',primary['methodOracleReviewSha256'])
    fields=data.read_checked(SUBJECT/'golden-field-map.json',primary['goldenFieldMapSha256'])
    assert len(records)==8 and Counter(Path(r['sourcePath']).stem for r in records)==Counter(HeaderModelTest=7,MessageCodecTest=1)
    manifest=data.read_checked(BASE/'PG9592-current-test-method-post-v1/manifest.json','d73ffe203a58ca9fab7f19f0b4baa7b2588fb25ad7e13c75c0c6411f5a719a18')
    methods=data.read_checked(BASE/'PG9592-current-test-method-post-v1/method-declaration-bindings.json',manifest['bindingsSha256'])
    by_key={r['methodDeclarationKey']:r for r in methods};ids=set();relations=0
    for record in records:
        method=by_key[record['methodDeclarationKey']]
        assert record['sourcePath']==method['path'] and record['sourceSha256']==method['sourceSha256']
        assert record['startLine']==method['startLine'] and record['endLine']==method['endLine'] and record['compiledDescriptor']==method['compiledDescriptor']=='()V'
        assert record['physicalTestClassSha256']==method['physicalClassSha256'] and record['fileCanonicalOwner']==method['fileCanonicalOwner']
        assert not record['productExecuted'] and not record['oldDynamicResultsTransferred']
        for reference in record['oracleReferences']:
            raw=(ROOT/reference['path']).read_bytes();assert data.sha(raw)==reference['sha256']
            line=raw.decode().splitlines()[reference['line']-1]
            assert data.sha(line.encode())==reference['rowSha256']
            assert line.startswith('| '+reference['existingTestId']+' |') or line.startswith(reference['existingTestId']+'：')
            ids.add(reference['existingTestId']);relations+=1
    assert len(ids)==primary['existingDistinctTestIdFamilies']==6 and relations==primary['methodTestIdRelations']==9
    canonical=primary['canonicalDesignCommit'];designs={}
    for path,digest in primary['canonicalDesignHashes'].items():
        raw=subprocess.check_output(['git','show',canonical+':'+path],cwd=ROOT);assert data.sha(raw)==digest;designs[path]=raw.decode()
    ui=next(text for path,text in designs.items() if '/232_' in path);ui_fields=[]
    for line in ui.splitlines():
        parts=[s.strip() for s in line.split('|')[1:-1]]
        if len(parts)==9 and parts[0].isdigit() and 1<=int(parts[0])<=17:
            n=int(parts[0]);start=int(parts[2]);end=int(parts[3]);length=int(parts[4]);assert end==start+length-1
            ui_fields.append((n,start,end,length))
    assert len(ui_fields)==17 and [r[0] for r in ui_fields]==list(range(1,18))
    expected_fields=[]
    for n,start,end,length in ui_fields:
        field=fields[n-1];assert end<=256
        expected_fields.append(dict(number=n,uiStart=start,length=length,offset=start-1,meaning=field['meaning']))
    validate(fields,expected_fields)
    assert fields[0]['offset']==0 and fields[-1]['offset']+fields[-1]['length']==256
    uuid='123e4567-e89b-12d3-a456-426614174000';literals=[
      'SCHBNK01','001','LGNREQ01','001','Q','S',uuid,uuid,'20260902123456789',' '*64,
      '0256','000384','000000','000000','000000640',' '*4,' '*44]
    expected=b''.join(value.encode('ascii') for value in literals)
    assert len(expected)==256 and data.sha(expected)==primary['staticGoldenReconstructionSha256']
    assert all(len(value.encode('ascii'))==row['length'] for value,row in zip(literals,fields))
    golden=next(r for r in records if Path(r['sourcePath']).stem=='MessageCodecTest')
    source=(ROOT/golden['sourcePath']).read_text().splitlines();body=source[golden['startLine']-1:golden['endLine']]
    reconstructed=bytearray(b' '*256);assignments=0
    for line in body:
        text=line.strip()
        if not text.startswith('ascii(expected,'):continue
        assert text.endswith(');');target,position,expression=text[len('ascii('):-2].split(',',2)
        assert target=='expected';position=int(position.strip());expression=expression.strip()
        value=(uuid if expression=='MESSAGE_ID.toString()' else json.loads(expression)).encode('ascii')
        assert 0<=position<=256-len(value);reconstructed[position:position+len(value)]=value;assignments+=1
    assert assignments==13 and bytes(reconstructed)==expected
    assert 1_000_000-256==999_744 and 256+9+272==537 and 256+384==640
    # Bind all six current executable Main identities to already independently read normal bytes.
    class_manifest=data.read_checked(BASE/'PG9564-g07-host-main-class-provenance-v1/manifest.json','458970306a06b661c558c67f25b5769308fffb91d2c7d8603f996084a70de2ff')
    proofs=data.read_checked(BASE/'PG9564-g07-host-main-class-provenance-v1/public-main-class-proofs.json',class_manifest['publicClassProofsSha256'])
    proof_by_class={p['className']:p for p in proofs}
    for key,row in primary['reviewedCurrentMainClasses'].items():
        proof=proof_by_class[key];assert proof['sha256']==row['sha256'] and proof['sourcePath']==row['path'] and proof['source']==SOURCE
    assert len(primary['reviewedCurrentMainClasses'])==6
    assert all(data.sha((ROOT/p).read_bytes())==data.sha((data.NORMAL/p).read_bytes())==h for p,h in primary['sourceHashes'].items())
    rejected=[]
    for label,edit in (('missing-field',lambda x:x.pop()),('offset',lambda x:x[0].update(offset=1)),
      ('length',lambda x:x[-1].update(length=43)),('source-index',lambda x:x[0].update(uiStart=0)),
      ('duplicate-field',lambda x:x.append(copy.deepcopy(x[0])))):
        changed=copy.deepcopy(fields);edit(changed)
        try:validate(changed,expected_fields)
        except ValueError:rejected.append(label)
        else:raise AssertionError('unproved UI field mapping accepted')
    for label,edit in (('wrong-ID',lambda x:x[0]['oracleReferences'][0].update(existingTestId='INVENTED001')),
      ('runtime-invented',lambda x:x[0].update(productExecuted=True)),('old-source-PT',lambda x:x[0].update(oldDynamicResultsTransferred=True)),
      ('method-position',lambda x:x[0].update(startLine=0)),('wrong-owner',lambda x:x[0].update(fileCanonicalOwner='WBS-P005-01'))):
        changed=copy.deepcopy(records);edit(changed)
        try:validate(changed,records)
        except ValueError:rejected.append(label)
        else:raise AssertionError('invalid method review record accepted')
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    verify(invocation);OUT.mkdir()
    value=dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      subjectManifestSha256=SUBJECT_SHA,staticMethodOracleRelationsVerified=8,existingDistinctTestIdFamilies=6,methodTestIdRelations=9,
      canonicalUiFields=17,independentStaticGoldenSha256=data.sha(expected),testBuilderAssignments=13,independentArithmeticVectors=3,
      currentMainClassProofs=6,metadataCounterexamples=rejected,semanticReviewIsParentRecordNotIndependentDynamicTest=True,
      actualProductionEncodingExecuted=False,productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,
      formalUpdated=False,newAccepted=0,effortPercent=None,wholeG13Accepted=False,whole451Accepted=False,
      wholeQseOrAllLayoutsQualified=False)
    data.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,methods=8,canonicalUiFields=17,metadataCounterexamples=len(rejected))))
    print('manifestSha256='+data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
